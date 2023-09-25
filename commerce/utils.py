import json
from . models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items = []
    order = {
        'get_cart_total':0,
        "get_cart_items":0}
    cart_items = order['get_cart_items']
    for i in cart:
        try:
            cart_items += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product':{ 
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'image': product.image
                },
                'quantity':cart[i]['quantity'],
                'get_total':total,
            }
            items.append(item)

            if product.digital == False:
                order["shipping"]=True  
        except:
            pass
    return {'cart_items': cart_items, 'order': order, 'items':items}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer, complete=False)
        if orders.exists():
    # Decide which order to use based on your application's logic
            order = orders.first()  # Use the first order, for example
        else:
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
        status = True
    else:
        cookie_data = cookieCart(request)
        cart_items = cookie_data['cart_items']
        items = cookie_data['items']
        order = cookie_data['order']
        status = False
    return {'cart_items': cart_items, 'order': order, 'items':items, 'status': status}

def guestOrder(request,data):
    print("User is not logged in")
    print("Cookies: ", request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']
    phone_number = data['form']['phone_number']
    

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,phone_number=phone_number,

    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        order_item = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    return customer,order
