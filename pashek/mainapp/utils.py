from django.db import models


def recalc_cart(cart):
    # звертається до всіх продуктів в цій корзині і рахує final_price
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data.get('final_price__sum')
    else:
        cart.final_price = 0
    # рахує кількість продуктів в корзині
    cart.total_products = cart_data['id__count']
    cart.save