from django.shortcuts import render
from .models import *
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.urls import reverse

# Create your views here.
def cart(request):
    data = cartData(request)
    cart_items = data['cart_items']
    items = data['items']
    order = data['order']
    status = data['status']
    context = {
        'items': items,
        "order": order,
        "cartItems": cart_items,
        'status': status
    }
    return render(request,template_name="commerce/cart.html",context=context)


def checkout(request):
    data = cartData(request)
    cart_items = data['cart_items']
    items = data['items']
    order = data['order']
    status = data['status']
    context = {
        'items': items,
        "order": order,
        "cartItems": cart_items,
        'status': status
    }
    return render(request,template_name="commerce/checkout.html",context=context)


def store(request):
    data = cartData(request)
    cart_items = data['cart_items']
    status = data['status']

    products = Product.objects.all()
    context = {
        'products':products, 'cartItems': cart_items,'status': status
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

from django.contrib.auth.models import User

def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "commerce/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create a new user
        try:
            # Create a new User instance
            user = User.objects.create_user(username=name, email=email, password=password)
            user.save()

            # Create a new Customer instance associated with the user
            customer = Customer(user=user, name=name, email=email, phone_number=phone_number)
            customer.save()

            # Log in the user
            login(request, user)

            return HttpResponseRedirect(reverse("store"))

        except IntegrityError:
            return render(request, "commerce/register.html", {
                "message": "Username already taken."
            })

    else:
        return render(request, "commerce/register.html")

    
def login_view(request):
    if request.method == "POST":


        # Attempt to sign user in
        name = request.POST["name"]
        password = request.POST["password"]
        user = authenticate(request, username=name, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("store"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "commerce/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("store"))