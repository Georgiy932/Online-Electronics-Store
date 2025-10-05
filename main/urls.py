from django.urls import path, include
from .views import home, about, contact, product_search, order_history, register
from .views import CustomLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('products/', include('phones.urls')),
    path('contact/', contact, name='contact'),
    path('search/', product_search, name='product_search'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('account/login/', CustomLoginView.as_view(), name='login'),
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('account/register/', register, name='register'),
    path('account/orders/', order_history, name='order_history'),
    path('order-history/', order_history, name='order_history'),
]