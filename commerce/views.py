from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder


# Create your views here.
def cart(request):
    data = cartData(request)
    cart_items = data['cart_items']
    items = data['items']
    order = data['order']
    context = {
        'items': items,
        "order": order,
        "cartItems": cart_items
    }
    return render(request,template_name="commerce/cart.html",context=context)


def checkout(request):
    data = cartData(request)
    cart_items = data['cart_items']
    items = data['items']
    order = data['order']
    context = {
        'items': items,
        "order": order,
        "cartItems": cart_items
    }
    return render(request,"commerce/checkout.html",context)


def store(request):
    data = cartData(request)
    cart_items = data['cart_items']

    products = Product.objects.all()
    context = {
        'products':products, 'cartItems': cart_items,
    }
    return render(request,"commerce/store.html",context)

def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    # print("Action: ", action, "productId:", productId)

    customer = request.user.customer 
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
         orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
       
    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    print("Processing order")
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer, complete=False)
        if orders.exists():
    # Decide which order to use based on your application's logic
            order = orders.first()  # Use the first order, for example
        else:
            order, created = Order.objects.get_or_create(customer=customer, complete=False)    

    else:
        customer,order = guestOrder(request,data)
    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    print("Total: ", type(total), "Cart_total:", type(order.get_cart_total))
    if total == float(order.get_cart_total):
        print("he order should be completed..")
        order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            country=data['shipping']['zipcode']
        )
    return JsonResponse("payment complete...", safe=False) 