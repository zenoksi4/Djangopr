from django.db import transaction
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View

from .models import Category, Customer, Order, CartProduct, Product
from .mixins import CartMixin
from .forms import OrderForm, LoginForm, RegistrationForm
from .utils import recalc_cart


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        products = Product.objects.all()
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart
        }
        return render(request, 'base.html', context)


class ProductDetailView(CartMixin, DetailView):

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


#створення урла категоріям

class CategoryDetailView(CartMixin, DetailView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        return context


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, product=product
        )
        if created:
            self.cart.products.add(cart_product)
        #методом save з models.Cart обновляє інфу в корзині тільки коли щось додається в корзину
        recalc_cart(self.cart)
        #Повідомлення в корзині що товар доданий
        #messages.add_message(request, messages.INFO, "Товар успішно доданий")
        return HttpResponseRedirect('/cart/')

class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )

        self.cart.products.remove(cart_product)
        cart_product.delete()
        #методом save з models.Cart обновляє інфу в корзині тільки коли щось удаляэться з корзини
        recalc_cart(self.cart)
        #Повідомлення в корзині що товар видалений
        messages.add_message(request, messages.INFO, "Товар успішно видалений")
        return HttpResponseRedirect('/cart/')

#Представлення зміни кол-ва товарів
class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        #Повідомлення в корзині що кол-во товару змінено
        messages.add_message(request,messages.INFO, "Кількість товару успішно змінено")
        return HttpResponseRedirect('/cart/')



class CartView(CartMixin, View):
    # відображення корзини та передача в cart.html
    def get(self, request, *args, **kwargs):
            categories = Category.objects.all()
            context = {
                'cart': self.cart,
                'categories': categories
            }
            return render(request, 'cart.html', context)


class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'checkout.html', context)

#Створення замовлення
class MakeOrderView(CartMixin, View):

    @transaction.atomic #все що проходить маэ пройти коректно або все выдкатиться
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Дякую за замовлення!')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')

class LoginView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        categories = Category.objects.all()
        context = {'form': form, 'categories': categories, 'cart': self.cart}
        return render(request, 'login.html', context)

    #відправка данних
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        context = {'form': form, 'cart': self.cart}
        return render(request, 'login.html', context)

class RegistrationView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        categories = Category.objects.all()
        #контекст для визова в шаблоні html
        context = {'form': form, 'categories': categories, 'cart': self.cart}
        return render(request, 'registration.html', context)

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            #зоздається новий обєкт
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            #покупець
            Customer.objects.create(
                user=new_user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address']
            )
            #аунтифікація користувача
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('/')
        context = {'form': form, 'cart': self.cart}
        return render(request, 'registration.html', context)

#представлення профілю користувача
class ProfileView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)

        #створення ордерів і їх впорядкування від останнього створенного до нового
        orders = Order.objects.filter(customer=customer).order_by('-created_at')

        categories = Category.objects.all()
        return render(
            request,
            'profile.html',
            {'orders': orders, 'cart': self.cart, 'categories': categories}
        )