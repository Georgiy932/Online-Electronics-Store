#views
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Wishlist, Cart, Order, CartItem
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import OrderForm
import requests
import json
import base64
import hashlib
from django.conf import settings
from django.http import HttpResponse
from liqpay.liqpay import LiqPay


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'phones/product_list.html', {'products': products, 'categories': categories})

def product_list_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    return render(request, 'phones/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    images = product.images.all()

    return render(request, "phones/product_detail.html", {
        "product": product,
        "images": images,
        "hide_categories": True,
    })


@login_required
def wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'phones/wishlist.html', {'wishlist': wishlist, "hide_categories": True})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if product in wishlist.products.all():
        wishlist.products.remove(product)  # Удаляем, если уже есть
    else:
        wishlist.products.add(product)  # Добавляем, если нет

    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.get(user=request.user)
    wishlist.products.remove(product)
    return redirect('wishlist')

@csrf_exempt
@login_required
def toggle_wishlist_ajax(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        if product in wishlist.products.all():
            wishlist.products.remove(product)
            in_wishlist = False
        else:
            wishlist.products.add(product)
            in_wishlist = True

        return JsonResponse({"success": True, "in_wishlist": in_wishlist})

    return JsonResponse({"success": False})


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'phones/cart.html', {'cart': cart, "hide_categories": True})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1  # Если товар уже есть, увеличиваем количество
        cart_item.save()

    # Определяем, куда редиректить (по умолчанию остаётся на текущей странице)
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', 'cart_view'))

    return redirect(next_url)


@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    return redirect('cart_view')


@login_required
def clear_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart.products.clear()
    return redirect('cart_view')


@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)

    if not cart.cart_items.exists():
        return redirect('cart_view')

    warehouses = []

    if request.method == "POST":
        form = OrderForm(request.POST)
        city_ref = request.POST.get("city_ref")
        payment_method = request.POST.get("payment_method")

        if city_ref:
            warehouses = get_warehouses(city_ref)

        if form.is_valid():
            branch_number = request.POST.get("warehouse_ref")
            if not branch_number:
                form.add_error(None, "Please select a delivery location.")
            else:
                order = form.save(commit=False)
                order.user = request.user
                order.total_price = cart.total_price()
                order.city_ref = city_ref
                order.warehouse_ref = branch_number
                order.save()
                order.products.set([item.product for item in cart.cart_items.all()])
                cart.cart_items.all().delete()

                # ⏩ если выбран online-платёж — отправляем на форму оплаты
                if payment_method == 'online':
                    return redirect('generate_payment_form', order_id=order.id)


                return redirect('order_success')
    else:
        form = OrderForm()

    return render(request, 'phones/checkout.html', {
        'form': form,
        'cart': cart,
        'warehouses': warehouses,
        "hide_categories": True
    })


def order_success(request):
    return render(request, "phones/order_success.html",{"hide_categories": True})

API_KEY = "685c17a7b9d856b46c31565fab135897"
NP_API_URL = "https://api.novaposhta.ua/v2.0/json/"


def get_cities(city_name):
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getCities",
        "methodProperties": {
            "FindByString": city_name
        }
    }
    response = requests.post(NP_API_URL, json=payload)
    return response.json()


# Отримання відділень
def get_warehouses(city_ref, type_ref=None):
    payload = {
        "apiKey": API_KEY,
        "modelName": "Address",
        "calledMethod": "getWarehouses",
        "methodProperties": {
            "CityRef": city_ref
        }
    }
    if type_ref:  # Для поштоматів
        payload["methodProperties"]["TypeOfWarehouseRef"] = type_ref

    response = requests.post(NP_API_URL, json=payload)
    return response.json()



@csrf_exempt
def search_cities(request):
    if request.method == "POST":
        city_name = request.POST.get("city_name", "")
    elif request.method == "GET":
        city_name = request.GET.get("q", "")  # или "city_name" — зависит от фронта
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

    cities = get_cities(city_name)
    return JsonResponse(cities)



# Отримання відділень з фільтрацією
@csrf_exempt
def get_departments(request):
    if request.method == "GET":
        city_ref = request.GET.get("city_ref")
        search_query = request.GET.get("search", "")

        payload = {
            "apiKey": API_KEY,
            "modelName": "Address",
            "calledMethod": "getWarehouses",
            "methodProperties": {"CityRef": city_ref}
        }

        response = requests.post(NP_API_URL, json=payload)
        departments = response.json().get('data', [])

        departments = [
            dept for dept in departments
            if dept.get('CategoryOfWarehouse') == 'Branch'
        ]

        if search_query:
            search_query = search_query.lower()
            departments = [
                dept for dept in departments
                if search_query in dept['Description'].lower() or search_query in dept['Number']
            ]

        return JsonResponse({"data": departments})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


# Отримання поштоматів з фільтрацією
@csrf_exempt
def get_postomats(request):
    if request.method == "POST":
        city_ref = request.POST.get("city_ref")
        search_query = request.POST.get("search", "")

        payload = {
            "apiKey": API_KEY,
            "modelName": "Address",
            "calledMethod": "getWarehouses",
            "methodProperties": {
                "CityRef": city_ref,
                "TypeOfWarehouseRef": "f9316480-5f2d-425d-bc2c-ac7cd29decf0"  # ID для поштоматів
            }
        }

        response = requests.post(NP_API_URL, json=payload)
        postomats = response.json().get('data', [])

        # Фільтрація за пошуком
        if search_query:
            search_query = search_query.lower()
            postomats = [
                postomat for postomat in postomats
                if search_query in postomat['Description'].lower() or search_query in postomat['Number']
            ]

        return JsonResponse({"data": postomats})


def generate_payment_form(request, order_id):
    from .models import Order  # если ещё не импортировал
    order = get_object_or_404(Order, id=order_id)

    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)

    data = {
        "action": "pay",
        'amount': str(round(order.total_price, 2)),
        "currency": "UAH",
        "description": f"Оплата заказа №{order.id}",
        "order_id": str(order.id),
        "version": "3",
        "language": "uk",
        "sandbox": 1,
        "result_url": request.build_absolute_uri('/payment/result/'),
        "server_url": request.build_absolute_uri('/payment/callback/')
    }

    signature = liqpay.cnb_signature(data)
    import pprint
    pprint.pprint(data)
    data_encoded = liqpay.cnb_data(data)

    return render(request, 'phones/payment_form.html', {
        'data': data_encoded,
        'signature': signature,
        "hide_categories": True
    })


@csrf_exempt
def liqpay_callback(request):
    if request.method == "POST":
        data = request.POST.get("data")
        signature = request.POST.get("signature")
        computed_signature = base64.b64encode(
            hashlib.sha1(
                settings.LIQPAY_PRIVATE_KEY.encode() +
                data.encode() +
                settings.LIQPAY_PRIVATE_KEY.encode()
            ).digest()
        ).decode()

        if signature == computed_signature:
            decoded_data = json.loads(base64.b64decode(data).decode())
            if decoded_data['status'] == 'success':
                order_id = decoded_data['order_id']
                from orders.models import Order
                order = Order.objects.get(id=order_id)
                order.is_paid = True
                order.save()

    return HttpResponse("OK")
