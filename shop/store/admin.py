from django.contrib import admin
from .models import Category, Product #, Customer           # modelsdagi classlarni chaqirdik

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'category', 'created_at', 'price', 'quantity') # admin panelga kirganda shu ma'lumotlar ko'rinishi uchun
    list_display_links = ('pk', 'name')    # pk va name xam link bo'lsin


# admin.site.register(Customer)                                 # adminga registratsiya qildik
admin.site.register(Category)
admin.site.register(Product)
