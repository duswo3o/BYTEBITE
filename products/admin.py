from django.contrib import admin
from .models import Product, PurchasedProduct


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")


@admin.register(PurchasedProduct)
class PurchasedProductAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "merchant_uid", "price", "status")
    list_editable = ("status",)
    search_fields = ("merchant_uid", "user__username", "product__name")
    list_filter = ("status",)
