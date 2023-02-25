from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Category, Product, Mail, Review, Favourite, ShippingAddress
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
# Create your views here.
from shop import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login, logout
from .forms import LoginForm, RegistrationForm, ReviewForm, ShippingForm
from .utils import CartForAuthenticatedUser
import stripe


class MainPage(ListView):
    model = Product
    template_name = 'store/main_page.html'
    context_object_name = 'products'


def shop_view(request):
    category__slug = request.GET.get('category')
    if category__slug:
        products = Product.objects.filter(category__slug=category__slug)
    else:
        products = Product.objects.all()
    count_products = len(products)

    sort = request.GET.get('sort')
    if sort:
        products = products.order_by(sort)
    paginator = Paginator(products, 2)
    page_number = request.GET.get('page')
    if page_number:
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = paginator.get_page(1)
    context = {
        'count_products': count_products,
        'products': page_obj.object_list,
        'page_obj': page_obj
    }
    return render(request, 'store/shop.html', context)


def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    products = Product.objects.all()
    reviews = Review.objects.filter(product=product)

    context = {
        'product': product,
        'products': products[:4],
        'reviews': reviews
    }
    if request.user.is_authenticated:
        context['review_form'] = ReviewForm()
    return render(request, 'store/detail.html', context)


# Сортировка на странице shop по цене названию
# переключение страниц на странице shop
# Повесить ссылки на категории
# Сделать умные ссылки в моделях
# Сделать рассылку по почте пользователям
# Сделать логин и регистрацию
# Отзывы (самостоятельная)
# Рэйтинг у товаров и соответственно у отзывов
# В навбаре подключить нормальные ссылки, везде

def save_mail(request):
    email = request.POST.get('email')
    if email:
        mail, created = Mail.objects.get_or_create(mail=email)
    return redirect('index')


def send_mail_to_users(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        mail_list = Mail.objects.all()
        for email in mail_list:
            mail = send_mail(
                subject='У нас новая акция',
                message=text,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
            )
            print(f'Отправлено ли сообщение на почту {email}? - {bool(mail)}')

    else:
        pass
    return render(request, 'store/send_mail.html')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли в аккаунт')
            return redirect('index')
        else:
            messages.error(request, 'Не верное имя пользователя/пароль')
            return redirect('login')



def user_logout(request):
    logout(request)
    # messages.warning(request, 'Вы вышли из аккаунта')
    return redirect('index')


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация прошла успешно. Войдите в аккаунт')
            return redirect('login')
        else:
            for field in form.errors:
                messages.error(request, form.errors[field].as_text())
            return redirect('register')


def save_review(request, slug):
    form = ReviewForm(data=request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = Product.objects.get(slug=slug)
        review.user = request.user
        review.save()
        return redirect('product', slug)


def add_to_favourite(request, slug):
    user = request.user
    product = Product.objects.get(slug=slug)

    favourite_products = Favourite.objects.filter(user=user)

    if product in [i.product for i in favourite_products]:
        fav_product = Favourite.objects.get(user=user, product=product)
        fav_product.delete()
    else:
        Favourite.objects.create(user=user, product=product)
    next_page = request.META.get('HTTP_REFERER', 'index')
    return redirect(next_page)


def favourite_view(request):
    favs = Favourite.objects.filter(user=request.user)
    products = [i.product for i in favs]
    context = {
        'products': products
    }
    return render(request, 'store/favourite.html', context)


def cart(request):
    cart_info = CartForAuthenticatedUser(request).get_cart_info()

    return render(request, 'store/cart.html', cart_info)


# Если купить несколько
def by_quantity(request, product_id, action):
    quantity = int(request.GET.get('quantity'))
    CartForAuthenticatedUser(request, product_id, action, quantity)
    return redirect('cart')


# Если +- 1
def to_cart(request, product_id, action, quantity):
    CartForAuthenticatedUser(request, product_id, action, quantity)
    return redirect('cart')


def checkout(request):
    cart_info = CartForAuthenticatedUser(request).get_cart_info()
    cart_info['form'] = ShippingForm()
    return render(request, 'store/checkout.html', cart_info)


def payment(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        user_cart = CartForAuthenticatedUser(request)
        cart_info = user_cart.get_cart_info()
        total_price = cart_info['cart_total_price']
        form = ShippingForm(data=request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.order = cart_info['order']
            address.save()
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Товары из Boutique'
                        },
                        'unit_amount': int(total_price * 100)
                    },
                    'quantity': 1
                }

            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('success')),
            cancel_url=request.build_absolute_uri(reverse('cart'))
        )
        return redirect(session.url, 303)



def success(request):
    user_cart = CartForAuthenticatedUser(request)
    user_cart.clear()
    return render(request, 'store/success.html')


