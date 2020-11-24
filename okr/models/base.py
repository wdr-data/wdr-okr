"""Base classes for database models."""

from django.db import models


class Product(models.Model):
    """Base model for products."""

    class Meta:
        """Model meta options."""

        abstract = True
        ordering = ["name"]

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Quintly(Product):
    """Base model for Quintly data."""

    class Meta:
        """Model meta options."""

        abstract = True
        ordering = Product.Meta.ordering

    quintly_profile_id = models.IntegerField()
