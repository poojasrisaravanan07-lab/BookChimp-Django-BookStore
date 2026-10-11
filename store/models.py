from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    """Book category e.g. Fiction, Non-fiction, Education, Tech."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Bootstrap icon class, e.g. 'bi-book'"
    )
    description = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("store:category_detail", args=[self.slug])


class Book(models.Model):
    """A single book listed in the store."""

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    author = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, related_name="books", on_delete=models.SET_NULL, null=True
    )
    description = models.TextField(
        help_text="Short description shown on the detail page."
    )
    ai_summary = models.TextField(
        blank=True,
        help_text="Cached AI-generated summary from Gemini. Leave blank to auto-generate on view."
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    cover_image = models.ImageField(upload_to="covers/", blank=True, null=True)
    cover_url = models.URLField(
        blank=True,
        help_text="Optional: external image URL, used if no image is uploaded."
    )
    isbn = models.CharField(max_length=20, blank=True)
    pages = models.PositiveIntegerField(default=0, blank=True)
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, default=4.0,
        help_text="Rating out of 5"
    )
    stock = models.PositiveIntegerField(default=25)

    is_bestseller = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_audiobook = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.author}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.author}")[:270]
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("store:book_detail", args=[self.slug])

    @property
    def display_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def has_discount(self):
        return bool(self.discount_price and self.discount_price < self.price)

    @property
    def discount_percent(self):
        if self.has_discount:
            return round((1 - (self.discount_price / self.price)) * 100)
        return 0

    @property
    def cover(self):
        """Return a usable image URL whether uploaded or external."""
        if self.cover_image:
            return self.cover_image.url
        if self.cover_url:
            return self.cover_url
        return ""

    @property
    def in_stock(self):
        return self.stock > 0


class Subscriber(models.Model):
    """Newsletter subscriber emails collected from the site."""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email


class FeaturedSection(models.Model):
    """Configurable homepage sections e.g. Best Sellers, New Arrivals."""

    SECTION_CHOICES = [
        ("bestseller", "Best Sellers"),
        ("new_arrival", "New Arrivals"),
        ("audiobook", "Audiobooks"),
        ("editor_pick", "Editor's Picks"),
    ]

    section_type = models.CharField(
        max_length=20, choices=SECTION_CHOICES, unique=True
    )
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=250, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.title


class Order(models.Model):
    """Dummy order created at checkout (no real payment processing)."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    book_title = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.book_title}"
