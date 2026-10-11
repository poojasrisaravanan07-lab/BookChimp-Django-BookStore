from decimal import Decimal
from .models import Book

CART_SESSION_KEY = "cart"


class Cart:
    """A simple session-based shopping cart (no login required)."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, book, quantity=1, override_quantity=False):
        book_id = str(book.id)
        if book_id not in self.cart:
            self.cart[book_id] = {
                "quantity": 0,
                "price": str(book.display_price),
                "title": book.title,
            }
        if override_quantity:
            self.cart[book_id]["quantity"] = quantity
        else:
            self.cart[book_id]["quantity"] += quantity
        self.save()

    def remove(self, book):
        book_id = str(book.id)
        if book_id in self.cart:
            del self.cart[book_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        book_ids = self.cart.keys()
        books = Book.objects.filter(id__in=book_ids)
        books_map = {str(b.id): b for b in books}

        for book_id, item in self.cart.items():
            book = books_map.get(book_id)
            if not book:
                continue
            item_copy = item.copy()
            item_copy["book"] = book
            item_copy["price"] = Decimal(item["price"])
            item_copy["total_price"] = item_copy["price"] * item["quantity"]
            yield item_copy

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def total_items(self):
        return len(self)

    @property
    def total_price(self):
        return sum(Decimal(item["price"]) * item["quantity"] for item in self.cart.values())
