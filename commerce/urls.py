from django.urls import path,include
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.store, name='store'),
    path("cart/",views.cart, name='cart'),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.update_item, name="update_item"),
    path("process_order/", views.processOrder, name="process_order"),
]