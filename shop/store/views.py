import stripe
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from .forms import LoginForm, RegistrationForm
from .models import Product, Category, Order, OrderProduct, Customer
from django.db.models import Q
from .utils import cart_data
from shop import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
class ProductList(ListView):
    model = Product
    extra_context = {
        'title': 'Главная страница'
    }

    context_object_name = 'categories'
    template_name = 'store/product_list.html'

    def get_queryset(self):
        categories = Category.objects.all()     # modelsdagi Category class ni xammasini chaqirdik
        data = []
        for category in categories:
            products = Product.objects.filter(
                category=category, is_published=True)[:4]    # category ustuni teng bo'sin category ga i topilganlarni 4tasini chiqar

            data.append({
                'title': category.title,
                'products': products
            })

        return data

    def get_context_data(self, object_list=None, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context["title"] = 'Главная страница'

        return context


class ProductListByCategory(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category_product_list.html'

    def get_queryset(self):
        sort_filed = self.request.GET.get('sorter')
        products = Product.objects.filter(category_id=self.kwargs['pk'])
        if sort_filed:
            products = products.order_by(sort_filed)

        return products


class SearchedProducts(ProductListByCategory):

    def get_queryset(self):
        searched_word = self.request.GET.get('q')
        products = Product.objects.filter(
            Q(name__icontains=searched_word) |
            Q(description__icontains=searched_word)
        )
        return products


class ProductDetail(DetailView):
    model = Product
    context_object_name = 'product'


def cart(request):
    data = cart_data(request)
    context = {
        'cart_products_quantity': data['cart_products_quantity'],
        'order': data['order'],
        'items': data['products']
    }
    return render(request, 'store/cart.html', context=context)


def checkout(request):
    cart = cart_data(request)
    context = {
        'cart_products_quantity': cart['cart_products_quantity'],
        'order': cart['order'],
        'items': cart['products'],
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    }

    return render(request, 'store/checkout.html', context=context)

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        cart = cart_data(request)
        YOUR_DOMAIN = 'http://127.0.0.1:8000/'
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(item['product']['price']) * 100,
                        'product_data': {
                            'name': item['product']['name'],
                            # 'images': ['url']
                        }
                    },
                    'quantity': item['quantity'] 
                } for item in cart['products']
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
        return JsonResponse({
            'id': checkout_session.id
        })



def add_or_delete_product_from_cart(request, product_id, action):
    product = Product.objects.get(pk=product_id)
    key = str(product_id)

    if not request.user.is_authenticated:
        session = request.session
        cart = session.get(settings.CART_SESSION_ID)

        if not cart:
            cart = session['cart'] = {}

        cart_product = cart.get(key)

        if action == 'add' and product.quantity > 0:
            if cart_product:
                cart_product['quantity'] += 1
            else:
                cart[key] = {
                    'quantity': 1
                }
            product.quantity -= 1

        elif action == 'delete':
            cart_product['quantity'] -= 1
            product.quantity += 1

            if cart_product['quantity'] <= 0:
                del cart[key]
        product.save()
        session.modified = True

    else:

        customer = request.user.customer

        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

        order_product, created = OrderProduct.objects.get_or_create(
            order=order, product=product)

        if action == 'add' and product.quantity > 0:
            order_product.quantity += 1
            product.quantity -= 1

        elif action == 'delete':
            order_product.quantity -= 1
            product.quantity += 1

        product.save()
        order_product.save()

        if order_product.quantity <= 0:
            order_product.delete()

    next_page = request.META.get('HTTP_REFERER', 'product_detail')
    return redirect(next_page)
# --------------- USERS START ---------------


def user_form(request):
    login_form = LoginForm()
    registration_form = RegistrationForm()

    context = {
        'login_form': login_form,
        'registration_form': registration_form
    }

    return render(request, 'store/user_form.html', context)


def user_login(request):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('product_list')
    else:
        messages.error(request, 'Неверное имя пользователя или пароль')
        return redirect('user_form')


def register(request):
    form = RegistrationForm(data=request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Отлично! Вы успршно зарегистрировались!')
    else:
        errors = form.errors
        messages.error(request, errors)
    return redirect('user_form')


def user_logout(request):
    logout(request)
    return redirect('product_list')


def profile(request):
    return render(request, 'store/profile.html')

# --------------- USERS END ---------------
