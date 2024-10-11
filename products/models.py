from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    price = models.PositiveIntegerField()
    image = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title
