from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.book_list, name="book_list"),
    path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("book/<slug:slug>/", views.book_detail, name="book_detail"),
    path("book/<slug:slug>/ai-summary/", views.fetch_ai_summary, name="fetch_ai_summary"),

    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:book_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:book_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:book_id>/", views.cart_remove, name="cart_remove"),

    path("checkout/", views.checkout, name="checkout"),
    path("order/<int:order_id>/success/", views.order_success, name="order_success"),

    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),

    path("signup/", views.signup, name="signup"),
    path("login/", views.StyledLoginView.as_view(), name="login"),
    path("logout/", views.StyledLogoutView.as_view(), name="logout"),

    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
