from .models import Customer, Order, Product
from shop import settings

# Bu funcsiya regitratsiyadan o'tmagan foydalanuvchi uchun KORZINKADA dobavit qilgan tavarini eslab qolish uchun
def get_session_cart(request):
    session = request.session
    cart = session.get(settings.CART_SESSION_ID)
                              # bu ^ kak localtsorage.Uni get orqali settingsdan olyabmiz
    if not cart:
        cart = session['cart'] = {
            # sessionda ^ card degan key ochyapmiz
        }
    items = []

    order = {
        'cart_total_price': 0,
        'cart_products_quantity': 0,
        'shipping': True,
    }
    cart_products_quantity = order['cart_products_quantity']

    for key in cart:
        if cart[key]['quantity'] > 0:
            print(cart)
            cart_products_quantity += cart[key]['quantity']
            product = Product.objects.get(pk=key)
            total_price = product.price * cart[key]['quantity']

            order['cart_products_quantity'] += cart[key]['quantity']
            order['cart_total_price'] +=  total_price

            item = {
                'pk': product.pk,
                'product': {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'image_url': product.image_url
                },
                'quantity': cart[key]['quantity'],
                'total_price': total_price
            }
            items.append(item)
    session.modified = True

    return {
        'order': order,
        'products': items,
        'cart_products_quantity': cart_products_quantity

    }


# Bu funcsiya agar foydalanuvchi registratsiyadan o'tgan bo'lsa data baza bn ishlayapdi, agar o'tmagan bo'lsa localStorage bn ishlayapdi
def cart_data(request):
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user, name=request.user.username, email=request.user.email)
# Bu get_or_create django ni narsasi. Unga 2ta o'zgaruvchi beriladi. Agar foyd.chi regist.dan o'tgan bo'lsa ob beradi yo'q bo'lsa yaratadi
    
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        products = order.orderproduct_set.all()
        cart_products_quantity = order.cart_products_quantity
      
    
    else: 
        session_cart = get_session_cart(request)
        order = session_cart['order']
        products = session_cart['products']
        cart_products_quantity = session_cart['cart_products_quantity']

    return {
        'order': order,
        'products': products,
        'cart_products_quantity':cart_products_quantity
    }
    
