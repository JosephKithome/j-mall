from django.urls import path
from .views import AddCoupon, CheckoutView, HomeView, ItemDetailView, OrderSummary, PaymentView, RequestRefundView,add_to_cart, remove_from_cart,remove_single_item_from_order


app_name = 'core'
urlpatterns=[
    path('',HomeView.as_view(),name='home'),
    path('product/<slug>/',ItemDetailView.as_view(),name='product'),
    path('add-to-cart/<slug>/',add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/',remove_from_cart, name="remove-from-cart"),
    path('order-summary',OrderSummary.as_view(), name="order-summary"),
    path('remove_single_item_from_order/<slug>/',remove_single_item_from_order, name="remove_single_item_from_order"),
    path('checkout/',CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/',PaymentView.as_view(),name='payment'),
    path('add-coupon/',AddCoupon.as_view(),name='add-coupon'),
    path('request-refund/',RequestRefundView.as_view(),name='request-refund'),
]