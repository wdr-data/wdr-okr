"""Database models for pages."""

from django.db import models
from pandas.io import html
from .base import Product


class Property(Product):
    """Grundlegende Website-Daten. Jeder Eintrag entspricht einer Property in der Google
    Search Console.

    Die Tabelle :model:`okr.Page` nimmt auf die in "ID" vergebenen Schlüssel (als
    foreign key namens ``property``) Bezug.
    """

    class Meta:
        """Model meta options."""

        db_table = "property"
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = Product.Meta.ordering

    url = models.URLField(
        verbose_name="URL",
        help_text="URL der Website",
        unique=True,
    )
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Datum der letzten Datenaktualisierung",
        auto_now=True,
    )


class Page(models.Model):
    """Grundlegende Daten einzelner Nachrichtenartikel.

    Verknüpft mit :model:`okr.Property` über den foreign key ``property``.

    Die folgenden Tabellen nehmen auf die in "ID"" vergebenen Schlüssel (als foreign key
    namens ``page``) Bezug:

    * :model:`okr.PageDataGSC`
    * :model:`okr.PageMeta`
    """

    class Meta:
        """Model meta options."""

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
        help_text="Globale ID der Website",
    )

    url = models.URLField(
        verbose_name="URL",
        help_text="URL des Nachrichtenartikels",
        unique=True,
    )
    sophora_id = models.CharField(
        verbose_name="Sophora ID",
        help_text="Sophora ID des Nachrichtenartikels",
        max_length=512,
    )
    sophora_page = models.IntegerField(
        verbose_name="Sophora-Seite",
        null=True,
        help_text="Mehrseitiger Nachrichtenartikel (nur falls zutreffend)",
    )
    first_seen = models.DateField(
        verbose_name="Zuerst gesehen",
        help_text="Erstellungsdatum des Datenpunktes",
        auto_now=True,
    )
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Jüngste Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.url} ({self.first_seen})"


class PageMeta(models.Model):
    """Metadaten zu einer individuellen Seite basierend auf Sophora-Daten.

    Verknüpft mit :model:`okr.Page` über den foreign key ``page``.
    """

    class Meta:
        """Model meta options."""

        db_table = "page_meta"
        verbose_name = "Seiten-Metadaten"
        verbose_name_plural = "Seiten-Metadaten"
        ordering = ["-editorial_update"]

    page = models.ForeignKey(
        to=Page,
        verbose_name="Seite",
        help_text="Globale ID des Nachrichtenartikels",
        on_delete=models.CASCADE,
        related_name="metas",
        related_query_name="meta",
        unique=True,
    )

    editorial_update = models.DateTimeField(
        verbose_name="Redaktioneller Stand",
        help_text="Von Redaktion gesetzes Standdatum",
        null=True,
    )
    headline = models.TextField(
        verbose_name="Titel",
        help_text="Schlagzeile des Nachrichtenartikels",
    )
    teaser = models.TextField(
        verbose_name="Teaser",
        help_text="Teasertext des Nachrichtenartikels",
    )
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return self.headline


class PageDataGSC(models.Model):
    """SEO-Performance pro Tag, basierend auf Daten der Google Search Console.

    Verknüpft mit :model:`okr.Page` über den foreign key ``page``.
    """

    class Meta:
        """Model meta options."""

        db_table = "page_data_gsc"
        verbose_name = "Seiten-Daten (GSC)"
        verbose_name_plural = "Seiten-Daten (GSC)"
        ordering = ["-date", "-clicks"]
        unique_together = ["date", "page", "device"]

    class DeviceType(models.TextChoices):
        """Available device types."""

        MOBILE = "MOBILE", "Mobil"
        DESKTOP = "DESKTOP", "Desktop"
        TABLET = "TABLET", "Tablet"

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der SEO-Daten",
    )
    page = models.ForeignKey(
        to=Page,
        verbose_name="Seite",
        help_text="Globale ID des Nachrichtenartikels",
        on_delete=models.CASCADE,
        related_name="data_gsc",
        related_query_name="data_gsc",
    )
    device = models.CharField(
        verbose_name="Gerätetyp",
        help_text="Gerätetyp (Mobil, Desktop oder Tablet)",
        choices=DeviceType.choices,
        max_length=16,
    )

    clicks = models.IntegerField(
        verbose_name="Klicks",
        help_text="Klicks (pro Tag)",
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        help_text="Impressions (pro Tag)",
    )
    ctr = models.FloatField(
        verbose_name="CTR",
        help_text="Click-Through Rate (pro Tag)",
    )
    position = models.FloatField(
        verbose_name="Position",
        help_text="Durchschnittliche Position in den Suchergebnissen",
    )
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Letzte Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.date} - {self.page.url}"
