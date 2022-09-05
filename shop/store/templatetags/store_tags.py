# bu Category larni chaqirib oladi.
# Boshqa joyda categoriyalarni ishlatsak get_categories deb foydalanib ketamiz

from django import template
from store.models import Category
from store.utils import cart_data

register = template.Library()

@register.simple_tag()
def get_categories():
    return Category.objects.all()


# Bu yog'i produktlarni sartirofka qilish
@register.simple_tag()
def get_sorters():
    info =  [
        {
            'title': 'По цене',
            'sorters': {
                ('price', 'По возростанию'),
                ('-price', 'По убыванию'),
            }
        },
        {
            'title': 'По дате добавления',
            'sorters': {
                ('created_at', 'Сначала старые'),
                ('-created_at', 'Сначала новые'),
            }
        },
        {
            'title': 'По названию',
            'sorters': {
                ('name', 'от А до Я'),
                ('-name', 'от Я до А'),
            }
        }
    ]
    
    return info


@register.simple_tag()
def get_cart_product_quantity(request):
    data = cart_data(request)
    return data['cart_products_quantity']