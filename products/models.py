from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Product(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    price = models.PositiveIntegerField()
    image = models.URLField(max_length=255, null=True, blank=True)
    consumer = models.ManyToManyField(
        User, related_name="basket", null=True, blank=True
    )

    def __str__(self):
        return self.name


class PurchasedProduct(models.Model):
    STATUS_SELECT = (
        ("A", "결제완료"),
        ("B", "배송대기"),
        ("C", "배송중"),
        ("D", "배송완료"),
    )

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="purchased"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    merchant_uid = models.CharField(max_length=50)
    price = models.PositiveIntegerField()
    address = models.CharField(max_length=100)
    address2 = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=1, choices=STATUS_SELECT, default="A")
