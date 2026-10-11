from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .ai_service import get_ai_summary
from .cart import Cart
from .forms import SubscriberForm, CheckoutForm, SignUpForm
from .models import Book, Category, FeaturedSection, Order, OrderItem


# ---------------------------------------------------------------------------
# HOME / STOREFRONT
# ---------------------------------------------------------------------------

def home(request):
    bestsellers = Book.objects.filter(is_bestseller=True)[:8]
    new_arrivals = Book.objects.filter(is_new_arrival=True).order_by("-created_at")[:8]
    audiobooks = Book.objects.filter(is_audiobook=True)[:8]
    featured = Book.objects.filter(is_featured=True)[:6]
    categories = Category.objects.all()[:8]
    sections = {s.section_type: s for s in FeaturedSection.objects.filter(is_active=True)}

    subscriber_form = SubscriberForm()

    context = {
        "bestsellers": bestsellers,
        "new_arrivals": new_arrivals,
        "audiobooks": audiobooks,
        "featured": featured,
        "categories": categories,
        "sections": sections,
        "subscriber_form": subscriber_form,
    }
    return render(request, "store/home.html", context)


def book_list(request):
    books = Book.objects.select_related("category").all()

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    sort = request.GET.get("sort", "")
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        books = books.filter(category=active_category)

    if sort == "price_low":
        books = books.order_by("price")
    elif sort == "price_high":
        books = books.order_by("-price")
    elif sort == "rating":
        books = books.order_by("-rating")
    elif sort == "newest":
        books = books.order_by("-created_at")

    if min_price:
        try:
            books = books.filter(price__gte=Decimal(min_price))
        except Exception:
            min_price = ""

    if max_price:
        try:
            books = books.filter(price__lte=Decimal(max_price))
        except Exception:
            max_price = ""

    paginator = Paginator(books, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "books": page_obj.object_list,
        "categories": Category.objects.all(),
        "active_category": active_category,
        "query": query,
        "sort": sort,
        "min_price": min_price,
        "max_price": max_price,
    }
    return render(request, "store/book_list.html", context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return redirect(f"{reverse_lazy('store:book_list')}?category={category.slug}")


def book_detail(request, slug):
    book = get_object_or_404(Book.objects.select_related("category"), slug=slug)
    related_books = Book.objects.filter(category=book.category).exclude(pk=book.pk)[:4]
    ai_summary = get_ai_summary(book)

    context = {
        "book": book,
        "related_books": related_books,
        "ai_summary": ai_summary,
    }
    return render(request, "store/book_detail.html", context)


@require_POST
def fetch_ai_summary(request, slug):
    """AJAX endpoint used to (re)generate the AI summary for a book."""
    book = get_object_or_404(Book, slug=slug)
    summary = get_ai_summary(book)
    return JsonResponse({"summary": summary})


# ---------------------------------------------------------------------------
# CART
# ---------------------------------------------------------------------------

def cart_detail(request):
    cart = Cart(request)
    return render(request, "store/cart_details.html", {"cart": cart})

@require_POST
def cart_add(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(book=book, quantity=quantity)
    messages.success(request, f"\u201c{book.title}\u201d was added to your cart.")
    next_url = request.POST.get("next") or "store:cart_detail"
    return redirect(next_url)



@require_POST
def cart_update(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect("store:cart_detail")

    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
    elif quantity > book.stock:
        messages.error(
            request,
            f"Only {book.stock} copies of {book.title} are available."
        )
    else:
        cart.add(book=book, quantity=quantity, override_quantity=True)
        messages.success(request, "Cart quantity updated successfully.")

    return redirect("store:cart_detail")


@require_POST
def cart_remove(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    messages.info(request, f"\u201c{book.title}\u201d was removed from your cart.")
    return redirect("store:cart_detail")


# ---------------------------------------------------------------------------
# CHECKOUT (dummy, no real payment)
# ---------------------------------------------------------------------------

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Add some books first!")
        return redirect("store:book_list")

    initial = {}
    if request.user.is_authenticated:
        initial = {"full_name": request.user.get_full_name() or request.user.username,
                   "email": request.user.email}

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total_amount = cart.total_price
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    book=item["book"],
                    book_title=item["book"].title,
                    price=item["price"],
                    quantity=item["quantity"],
                )
            cart.clear()
            return redirect("store:order_success", order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, "store/checkout.html", {"form": form, "cart": cart})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "store/order_success.html", {"order": order})


# ---------------------------------------------------------------------------
# NEWSLETTER
# ---------------------------------------------------------------------------

@require_POST
def newsletter_subscribe(request):
    form = SubscriberForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "\U0001F389 Thanks for subscribing to our newsletter!")
    else:
        if "email" in form.errors:
            messages.error(request, "That email is already subscribed or invalid.")
    return redirect(request.META.get("HTTP_REFERER", "store:home"))


# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to BookChimp, {user.username}!")
            return redirect("store:home")
    else:
        form = SignUpForm()
    return render(request, "store/signup.html", {"form": form})


class StyledLoginView(LoginView):
    template_name = "store/login.html"
    redirect_authenticated_user = True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Username"})
        form.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password"})
        return form


class StyledLogoutView(LogoutView):
    next_page = reverse_lazy("store:home")


# ---------------------------------------------------------------------------
# STATIC PAGES
# ---------------------------------------------------------------------------

def about(request):
    return render(request, "store/about.html")


def contact(request):
    if request.method == "POST":
        messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
        return redirect("store:contact")
    return render(request, "store/contact.html")
