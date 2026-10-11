from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Book, Subscriber, FeaturedSection, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "book_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = "Books"


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "cover_thumb", "title", "author", "category", "price",
        "discount_price", "stock", "rating",
        "is_bestseller", "is_new_arrival", "is_audiobook", "is_featured",
    )
    list_filter = ("category", "is_bestseller", "is_new_arrival", "is_audiobook", "is_featured")
    search_fields = ("title", "author", "isbn")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("price", "discount_price", "stock", "is_bestseller", "is_new_arrival", "is_audiobook", "is_featured")
    readonly_fields = ("created_at", "updated_at", "cover_preview")

    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "slug", "author", "category", "isbn", "pages")
        }),
        ("Description & AI Summary", {
            "fields": ("description", "ai_summary"),
            "description": "Leave 'ai_summary' blank to auto-generate it via Gemini when a customer views the book."
        }),
        ("Pricing & Stock", {
            "fields": ("price", "discount_price", "stock", "rating")
        }),
        ("Cover Image", {
            "fields": ("cover_image", "cover_url", "cover_preview")
        }),
        ("Featured Sections", {
            "fields": ("is_bestseller", "is_new_arrival", "is_audiobook", "is_featured")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def cover_thumb(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" style="height:45px;width:32px;object-fit:cover;border-radius:4px;" />',
                obj.cover
            )
        return "—"
    cover_thumb.short_description = "Cover"

    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" style="height:180px;border-radius:8px;" />', obj.cover
            )
        return "No image set"
    cover_preview.short_description = "Preview"


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at", "is_active")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    list_editable = ("is_active",)


@admin.register(FeaturedSection)
class FeaturedSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "section_type", "is_active", "display_order")
    list_editable = ("is_active", "display_order")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("book", "book_title", "price", "quantity", "subtotal")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email")
    list_editable = ("status",)
    inlines = [OrderItemInline]
    readonly_fields = ("full_name", "email", "address", "phone", "total_amount", "user", "created_at")
