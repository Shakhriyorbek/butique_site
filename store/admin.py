from django.contrib import admin
from .models import Product, Category, Gallery, Mail

# Register your models here.

class GalleryInline(admin.TabularInline):
    fk_name = 'product'
    model = Gallery
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent')
    prepopulated_fields = {'slug': ('title', )}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'category', 'quantity', 'price', 'size', 'color')
    list_editable = ('price', 'quantity', 'size', 'color')
    list_display_links = ('title', )
    prepopulated_fields = {'slug': ('title', )}
    inlines = [GalleryInline]


admin.site.register(Mail)