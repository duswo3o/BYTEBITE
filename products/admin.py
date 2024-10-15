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

    # 모든 필드를 읽기 전용으로 설정
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 기존 객체일 경우 모든 필드 읽기 전용
            return [field.name for field in self.model._meta.fields]
        return []

    # 추가 권한 비활성화
    def has_add_permission(self, request):
        return False
