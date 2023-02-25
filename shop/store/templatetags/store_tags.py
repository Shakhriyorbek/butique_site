from django import template
from store.models import Category, Favourite

register = template.Library()

@register.simple_tag()
def get_categories():
    return Category.objects.filter(parent=None)


@register.simple_tag()
def get_sorters():
    sorters = [
        ['price', 'Цена: По возрастанию'],
        ['-price', 'Цена: По убыванию'],
        ['title', 'Название: А-Я'],
        ['-title', 'Название: Я-А'],
        ['quantity', 'Количество: Меньше'],
        ['-quantity', 'Количество: Больше'],
    ]
    return sorters


@register.simple_tag()
def get_favourite(user):
    favs = Favourite.objects.filter(user=user)
    products = [i.product for i in favs]
    return products






