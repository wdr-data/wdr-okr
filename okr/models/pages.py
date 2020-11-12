from django.db import models
from pandas.io import html
from .base import Product


class Property(Product):
    """
    Parent object for pages of a particular website.
    Equivalent to a property in Google Search Console.
    """

    class Meta:
        db_table = "property"
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = Product.Meta.ordering

    url = models.URLField(verbose_name="URL", unique=True)
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)


class Page(models.Model):
    """
    Describes a single page and some of it's static metadata.
    Unique pages are identified by their URL.
    """

    class Meta:
        db_table = "page"
        verbose_name = "Seite"
        verbose_name_plural = "Seiten"
        ordering = ["-first_seen"]

    property = models.ForeignKey(
        to=Property,
        verbose_name="Property",
        on_delete=models.CASCADE,
        related_name="pages",
        related_query_name="page",
    )

    url = models.URLField(verbose_name="URL", unique=True)
    sophora_id = models.CharField(
        verbose_name="Sophora ID",
        max_length=512,
    )
    sophora_page = models.IntegerField(
        verbose_name="Sophora-Seite",
        null=True,
        help_text=(
            "Wenn unter der Sophora ID ein mehrseitiger Artikel ist "
            "und eine Unterseite besucht wird, steht hier ein Wert"
        ),
    )
    first_seen = models.DateField(verbose_name="Zuerst gesehen", auto_now=True)
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.url} ({self.first_seen})"


class PageMeta(models.Model):
    """
    Metadata about a page sourced from Sophora.
    """

    class Meta:
        db_table = "page_meta"
        verbose_name = "Seiten-Metadaten"
        verbose_name_plural = "Seiten-Metadaten"
        ordering = ["-editorial_update"]

    page = models.ForeignKey(
        to=Page,
        verbose_name="Seite",
        on_delete=models.CASCADE,
        related_name="meta",
        related_query_name="meta",
        unique=True,
    )

    editorial_update = models.DateTimeField(verbose_name="Redaktioneller Stand")
    headline = models.TextField(
        verbose_name="Titel",
    )
    teaser = models.TextField(
        verbose_name="Teaser",
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return self.headline


class PageDataGSC(models.Model):
    """
    Daily page SEO-performance statistics from Google Search Console.
    """

    class Meta:
        db_table = "page_data_gsc"
        verbose_name = "Seiten-Daten (GSC)"
        verbose_name_plural = "Seiten-Daten (GSC)"
        ordering = ["-date", "-clicks"]
        unique_together = ["date", "page", "device"]

    class DeviceType(models.TextChoices):
        MOBILE = "MOBILE", "Mobil"
        DESKTOP = "DESKTOP", "Desktop"
        TABLET = "TABLET", "Tablet"

    date = models.DateField(verbose_name="Datum")
    page = models.ForeignKey(
        to=Page,
        verbose_name="Seite",
        on_delete=models.CASCADE,
        related_name="data_gsc",
        related_query_name="data_gsc",
    )
    device = models.CharField(
        verbose_name="Gerätetyp", choices=DeviceType.choices, max_length=16
    )

    clicks = models.IntegerField(
        verbose_name="Klicks",
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
    )
    ctr = models.FloatField(
        verbose_name="CTR",
    )
    position = models.FloatField(
        verbose_name="Durchschnittliche Position",
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.page.url}"
