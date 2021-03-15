from django.views.generic import View
from .models import Cart, Customer



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
