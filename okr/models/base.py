"""Base classes for database models."""

from django.conf import settings
from django.db import models


class ActiveManager(models.Manager):
    """Custom Manager class that filters out inactive objects"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


def with_active_manager(cls):
    """
    Override default manager to only yield active objects.
    Should only happen in worker, since we don't want inactive objects to be
    filtered out in Django Admin.
    """
    default_manager = models.Manager()

    if settings.ROLE == "worker":
        cls.add_to_class("objects", ActiveManager())
    else:
        cls.add_to_class("objects", default_manager)

    cls.add_to_class("objects_all", default_manager)

    return cls


@with_active_manager
class Product(models.Model):
    """Base model for products."""

    class Meta:
        """Model meta options."""

        abstract = True
        ordering = ["name"]

    name = models.CharField(
        verbose_name="Name",
        help_text="Name des Objekts",
        max_length=200,
        unique=True,
    )

    is_active = models.BooleanField(
        verbose_name="Aktiv",
        help_text="Entscheidet darüber, ob die Scraper für dieses Objekt aktiv sind",
        default=True,
    )

    def __str__(self):
        return self.name


class Quintly(Product):
    """Base model for Quintly data."""

    class Meta:
        """Model meta options."""

        abstract = True
        ordering = Product.Meta.ordering

    quintly_profile_id = models.IntegerField(verbose_name="Quintly Profil-ID")
