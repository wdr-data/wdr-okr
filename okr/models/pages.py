"""Database models for pages."""

from django.db import models
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


class SophoraNode(models.Model):
    """Die Sophora-Datenbank wird anhand der Sophora-Knoten durchsucht, um neue und aktualisierte
    :model:`okr.SophoraDocument` zu finden.
    """

    class Meta:
        """Model meta options."""

        db_table = "sophora_node"
        verbose_name = "Sophora-Knoten"
        verbose_name_plural = "Sophora-Knoten"
        ordering = ["node"]

    node = models.CharField(
        verbose_name="Sophora Knoten",
        help_text='Sophora-Knoten in der Form "/wdr/nachrichten" (ohne trailing slash)',
        max_length=128,
        unique=True,
    )
    use_exact_search = models.BooleanField(
        verbose_name="Ignoriere Unterknoten",
        help_text="Wenn dieser Haken gesetzt ist, werden Unterknoten ignoriert",
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Jüngste Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return self.node


class SophoraDocument(models.Model):
    """Repräsentation eines einzelnen Dokuments in Sophora."""

    class Meta:
        """Model meta options."""

        db_table = "sophora_document"
        verbose_name = "Sophora-Dokument"
        verbose_name_plural = "Sophora-Dokumente"
        ordering = ["-created"]

    sophora_node = models.ForeignKey(
        to=SophoraNode,
        verbose_name="Sophora-Knoten",
        on_delete=models.CASCADE,
        related_name="documents",
        related_query_name="document",
        help_text="Der Sophora-Knoten, unter dem dieses Dokument gefunden wurde",
    )

    export_uuid = models.CharField(
        verbose_name="UUID",
        help_text="Die ID, die dem Dokument vom Export-System zugewiesen wurde",
        max_length=64,
        unique=True,
    )

    created = models.DateTimeField(
        verbose_name="Zeitpunkt der Erstellung",
        help_text="Der Zeitpunkt, an dem dieser Eintrag in der Datenbank angelegt wurde",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.export_uuid}"


class SophoraID(models.Model):
    """Speichert Sophora-IDs die zu einem Dokument gehörten."""

    sophora_document = models.ForeignKey(
        to=SophoraDocument,
        verbose_name="Sophora-Dokument",
        on_delete=models.CASCADE,
        related_name="sophora_ids",
        related_query_name="sophora_id",
        help_text="Das Sophora-Dokument, zu dem diese ID gehört (hat)",
    )

    sophora_id = models.CharField(
        verbose_name="Sophora ID",
        help_text="Sophora ID des Dokuments",
        max_length=128,
        unique=True,
    )

    created = models.DateTimeField(
        verbose_name="Zeitpunkt der Erstellung",
        help_text="Der Zeitpunkt, an dem dieser Eintrag in der Datenbank angelegt wurde",
        auto_now=True,
    )

    def __str__(self):
        return self.sophora_id


class SophoraDocumentMeta(models.Model):
    """Meta-Informationen zu einem bestimmten Dokument. Es kann mehrere Meta-Einträge zum selben
    Dokument geben, wenn z. B. die Überschrift geändert wird.
    """

    class Meta:
        """Model meta options."""

        db_table = "sophora_document_meta"
        verbose_name = "Sophora-Dokument-Meta"
        verbose_name_plural = "Sophora-Dokument-Metas"
        ordering = ["-created"]
        unique_together = (
            "sophora_document",
            "headline",
            "teaser",
            "document_type",
        )

    sophora_document = models.ForeignKey(
        to=SophoraDocument,
        verbose_name="Sophora-Dokument",
        on_delete=models.CASCADE,
        related_name="metas",
        related_query_name="meta",
        help_text="Das Sophora-Dokument, zu dem diese Daten gehören",
    )

    editorial_update = models.DateTimeField(
        verbose_name="Redaktioneller Stand",
        help_text="Von Redaktion gesetzes Standdatum",
        null=True,
    )
    node = models.CharField(
        verbose_name="Strukturknoten",
        help_text="Der Sophora-Strukturknoten, unter dem das Dokument momentan abgelegt ist",
        max_length=128,
    )
    sophora_id = models.CharField(
        verbose_name="Sophora ID",
        help_text="Momentane Sophora ID des Dokuments",
        max_length=128,
    )
    headline = models.TextField(
        verbose_name="Titel",
        help_text="Schlagzeile des Sophora-Dokuments",
    )
    teaser = models.TextField(
        verbose_name="Teaser",
        help_text="Teasertext des Sophora-Dokuments",
    )
    document_type = models.CharField(
        verbose_name="Beitragstyp",
        help_text="Der Typ des Sophora-Beitrags",
        max_length=64,
    )

    created = models.DateTimeField(
        verbose_name="Zeitpunkt der Erstellung",
        help_text="Der Zeitpunkt, an dem diese Metadaten abgerufen wurden",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.sophora_id} ({self.created})"


class Page(models.Model):
    """Grundlegende Daten einzelner URLs.

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
        help_text="Die GSC-Property, unter der diese Seite gefunden wurde",
    )
    sophora_document = models.ForeignKey(
        to=SophoraDocument,
        verbose_name="Sophora-Dokument",
        on_delete=models.CASCADE,
        related_name="pages",
        related_query_name="page",
        help_text="Das Sophora-Dokument, auf das diese Seite zeigt",
        null=True,
    )

    url = models.URLField(
        verbose_name="URL",
        help_text="URL des Nachrichtenartikels",
        unique=True,
        max_length=1024,
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
