from django.urls import path

from .views import *

urlpatterns = [
    path('', ProductList.as_view(), name='product_list'),
    path('category/<int:pk>/', ProductListByCategory.as_view(), name='product_list_by_category'),
    path('product/<int:pk>/', ProductDetail.as_view(), name='product_detail'),
    path('to-cart/<int:product_id>/<str:action>/', add_or_delete_product_from_cart, name='to_cart'),
    path('create-checkout-session',  CreateCheckoutSessionView.as_view(), name='create-checkout-session'),

    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('search/', SearchedProducts.as_view(), name='search'),

    path('login_register/', user_form, name='user_form'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('register/', register, name='register')
]
