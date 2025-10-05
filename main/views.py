from django.shortcuts import render, redirect
from phones.models import Category, Product, Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomAuthenticationForm

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'account/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_categories'] = True  # Добавляем в контекст
        return context

    def get_success_url(self):
        return '/'




def index(request):
    categories = Category.objects.all()
    return render(request, 'main/index.html', {'categories': categories})

def home(request):
    categories = Category.objects.all()
    hide_categories = request.GET.get("hide_categories") == "1"
    return render(request, 'main/index.html', {'categories': categories})


def about(request):
    categories = Category.objects.all()
    hide_categories = request.GET.get("hide_categories") == "1"
    return render(request, 'main/about.html', {'categories': categories, "hide_categories": True})

def contact(request):
    categories = Category.objects.all()
    hide_categories = request.GET.get("hide_categories") == "1"
    return render(request, 'main/contact.html', {'categories': categories, "hide_categories": True})

def product_search(request):
    query = request.GET.get('q', '')
    categories = Category.objects.all()
    products = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'main/product_search.html', {'products': products, 'query': query, 'categories': categories})

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, "account/register.html", {"form": form, "hide_categories": True})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'account/order_history.html', {'orders': orders, "hide_categories": True})



def custom_logout(request):
    logout(request)  # Выходим из системы
    return redirect('/')

