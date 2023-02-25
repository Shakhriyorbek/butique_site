from django.urls import path
from .views import *

urlpatterns = [
    path('', MainPage.as_view(), name='index'),
    path('shop/', shop_view, name='shop'),
    path('product/<slug:slug>', product_detail, name='product'),
    path('save_mail', save_mail, name='save_mail'),
    path('send_mail', send_mail_to_users, name='send_mail'),

    path('login', user_login, name='login'),
    path('logout', user_logout, name='logout'),
    path('register', register, name='register'),

    path('save_review/<slug:slug>/', save_review, name='save_review'),
    path('add_favourite/<slug:slug>/', add_to_favourite, name='add_favourite'),
    path('favourite/', favourite_view, name='favourite'),
    path('cart/', cart, name='cart'),
    path('buy_quantity/<int:product_id>/<str:action>/', by_quantity, name='buy_quantity'),
    path('to_cart/<int:product_id>/<str:action>/<int:quantity>', to_cart, name='to_cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/', payment, name='payment'),
    path('success/', success, name='success')

]