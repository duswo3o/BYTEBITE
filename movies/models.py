from django.db import models


# Create your models here.
class Ranking(models.Model):
    title = models.CharField(max_length=255)
    rank = models.PositiveIntegerField()
    crawling_date = models.DateField()

    def __str__(self):
        return self.title
