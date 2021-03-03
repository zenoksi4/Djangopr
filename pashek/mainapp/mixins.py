from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View
from .models import Category, Cart, Customer, Notebook, Smartphone



class CategoryDetailMixin(SingleObjectMixin):
    #slug ноутів категорій
    CATEGORY_SLUG2PRODUCT_MODEL = {
        'notebooks': Notebook,
        'smartphones': Smartphone
    }


    # вивід категорій на сторінці категорій
    def get_context_data(self, **kwargs):
        if isinstance(self.get_object(), Category):
            model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories_for_left_sidebar()
            context['category_products'] = model.objects.all()
            return  context
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.get_categories_for_left_sidebar()
        return context





class CartMixin(View):
    #створення корзин
    def dispatch(self, request, *args, **kwargs):
        #користувач зареестрований
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            #ненаход покупця
            if not customer:
                #як що ненаходе в користувача покупця то создає (Customer)
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
            #створення корзини як що її нема
                cart = Cart.objects.create(owner=customer)
        # користувач не зареестрований
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)
