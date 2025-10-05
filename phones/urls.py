from django.urls import path
from .views import product_list, product_list_by_category, product_detail, wishlist, add_to_wishlist, remove_from_wishlist, toggle_wishlist_ajax, cart_view, add_to_cart, remove_from_cart, clear_cart, checkout, order_success
from django.http import JsonResponse
from .views import get_departments, search_cities
from . import views


urlpatterns = [
    path('products/', product_list, name='product_list'),
    path('category/<slug:category_slug>/', product_list_by_category, name='product_list_by_category'),
    path('product/<slug:slug>/', product_detail, name="product_detail"),
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/toggle/', toggle_wishlist_ajax, name='toggle_wishlist_ajax'),
    path('cart/', cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('checkout/', checkout, name='checkout'),
    path('order_success/', order_success, name='order_success'),

    path('api/nova-poshta/search_cities/', views.search_cities),
    path('api/nova-poshta/warehouses/', views.get_departments),
    path('api/nova-poshta/cities/', views.search_cities),

    path('payment/<int:order_id>/', views.generate_payment_form, name='generate_payment_form'),
    path('payment/callback/', views.liqpay_callback, name='liqpay_callback'),
    path('payment/result/', views.order_success, name='order_success'),
]


