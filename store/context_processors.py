from .models import Category
from .cart import Cart


def cart_summary(request):
    cart = Cart(request)
    return {
        "cart_total_items": cart.total_items,
        "cart_total_price": cart.total_price,
    }


def site_categories(request):
    return {
        "nav_categories": Category.objects.all(),
    }
