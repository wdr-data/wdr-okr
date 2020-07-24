from django.db import models


class Product(models.Model):
    class Meta:
        abstract = True
        ordering = ["name"]

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Quintly(Product):
    class Meta:
        abstract = True
        ordering = Product.Meta.ordering

    quintly_profile_id = models.IntegerField()
