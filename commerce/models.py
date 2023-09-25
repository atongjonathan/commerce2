from django.db import models
from django.contrib.auth.models import User
import re
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser

class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, null=True, blank=True )
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(max_length=100, null=True)
    phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(null=True,blank=True)
    # Image
    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.id)
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping
    @property
    def get_cart_total(self):
        order_items = self.orderitem_set.all()
        total = sum(item.get_total for item in order_items)
        return total
    @property
    def get_cart_items(self):
        order_items = self.orderitem_set.all()
        total = sum(item.quantity for item in order_items)
        return total        
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    # def __str__(self) -> str:
    #     return self.id
    @property
    def get_total(self):
        total = self.quantity * self.product.price
        return total


class ShippingAddress(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=50, default="Kenya",null=True, blank=True)

    def __str__(self) -> str:
        return self.address


