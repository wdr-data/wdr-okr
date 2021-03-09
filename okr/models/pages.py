"""Database models for pages."""

from django.db import models
from .base import Product


class Property(Product):
    """Grundlegende Website-Daten. Jeder Eintrag entspricht einer Property in der Google
    Search Console.
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
    Sophora-Dokumente zu finden.
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
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.export_uuid}"


class SophoraID(models.Model):
    """Speichert Sophora-IDs, die zu einem Sophora-Dokument gehören. Enthält auch
    ehemalige Sophora-IDs, falls der ID-Stamm des Sophora-Dokuments geändert wurde.
    """

    class Meta:
        """Model meta options."""

        db_table = "sophora_id"
        verbose_name = "Sophora-ID"
        verbose_name_plural = "Sophora-IDs"
        ordering = ["-created"]

    sophora_document = models.ForeignKey(
        to=SophoraDocument,
        verbose_name="Sophora-Dokument",
        on_delete=models.CASCADE,
        related_name="sophora_ids",
        related_query_name="sophora_id",
        help_text="Das Sophora-Dokument, zu dem diese ID gehört (hat)",
        null=True,
    )

    sophora_id = models.TextField(
        verbose_name="Sophora ID",
        help_text="Sophora ID des Dokuments",
        unique=True,
    )

    created = models.DateTimeField(
        verbose_name="Zeitpunkt der Erstellung",
        help_text="Der Zeitpunkt, an dem dieser Eintrag in der Datenbank angelegt wurde",
        auto_now_add=True,
    )

    def __str__(self):
        return self.sophora_id


class SophoraDocumentMeta(models.Model):
    """Meta-Informationen zu einem bestimmten Sophora-Dokument. Es kann mehrere
    Meta-Einträge zum selben Dokument geben, wenn z. B. die Überschrift geändert wurde.
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
            "word_count",
            "document_type",
            "sophora_id",
            "node",
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
    sophora_id = models.ForeignKey(
        to=SophoraID,
        verbose_name="Sophora ID",
        on_delete=models.CASCADE,
        related_name="metas",
        related_query_name="meta",
        help_text="Momentane Sophora ID des Dokuments",
    )
    headline = models.TextField(
        verbose_name="Titel",
        help_text="Schlagzeile des Sophora-Dokuments",
    )
    teaser = models.TextField(
        verbose_name="Teaser",
        help_text="Teasertext des Sophora-Dokuments",
    )
    word_count = models.IntegerField(
        verbose_name="Word Count",
        null=True,
        help_text="Anzahl der Wörter im Fließtext (incl. Zwischenüberschriften)",
    )
    document_type = models.CharField(
        verbose_name="Beitragstyp",
        help_text="Der Beitragstyp des Sophora-Beitrags",
        max_length=64,
    )

    created = models.DateTimeField(
        verbose_name="Zeitpunkt der Erstellung",
        help_text="Der Zeitpunkt, an dem diese Metadaten abgerufen wurden",
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.sophora_id} ({self.created})"


class SophoraKeywords(models.Model):
    """Keywords ("tags"), die in Sophora-Dokumenten genutzt werden."""

    class Meta:
        """Model meta options."""

        db_table = "sophora_keywords"
        verbose_name = "Sophora-Keywords"
        verbose_name_plural = "Sophora-Keywords"
        ordering = ["-first_seen"]
        unique_together = ("keyword", "first_seen")

    sophora_documents = models.ManyToManyField(
        to=SophoraDocument,
        verbose_name="Sophora-Dokumente",
        db_table="sophora_document_meta_keywords",
        related_name="keywords",
        related_query_name="keyword",
        help_text="Die Sophora-Dokumente, die dieses Keyword nutzen.",
    )

    keyword = models.CharField(
        verbose_name="Keyword",
        help_text="Das Keyword",
        max_length=512,
    )

    first_seen = models.DateTimeField(
        verbose_name="Zeitpunkt der Erst-Erfassung",
        help_text="Der Zeitpunkt, zu dem dieses Keyword erstmals im Intelligence Layer erfasst wurde.",
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.keyword} ({self.first_seen})"


class Page(models.Model):
    """Grundlegende Daten einzelner URLs."""

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
    sophora_id = models.ForeignKey(
        to=SophoraID,
        verbose_name="Sophora ID",
        help_text="Sophora ID der Seite",
        on_delete=models.CASCADE,
        related_name="pages",
        related_query_name="page",
        null=True,
    )
    node = models.CharField(
        verbose_name="Strukturknoten",
        help_text="Der Sophora-Strukturknoten, unter dem der Nachrichtenartikel gefunden wurde",
        max_length=128,
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
        help_text="Seitennummer bei mehrseitigen Nachrichtenartikeln (nur falls zutreffend)",
    )
    first_seen = models.DateField(
        verbose_name="Zuerst gesehen",
        help_text="Erstellungsdatum des Datenpunktes",
        auto_now_add=True,
    )
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Jüngste Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.url} ({self.first_seen})"


class DataGSC(models.Model):
    """Basismodel für Daten der Google Search Console."""

    class Meta:
        """Model meta options."""

        abstract = True

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


class PropertyDataGSC(DataGSC):
    """SEO-Performance der gesamten Property pro Tag, basierend auf Daten der Google
    Search Console."""

    class Meta:
        """Model meta options."""

        db_table = "property_data_gsc"
        verbose_name = "Property-Daten (GSC)"
        verbose_name_plural = "Property-Daten (GSC)"
        ordering = ["-date", "-clicks"]
        unique_together = ["date", "property", "device"]

    class DeviceType(models.TextChoices):
        """Available device types."""

        MOBILE = "MOBILE", "Mobil"
        DESKTOP = "DESKTOP", "Desktop"
        TABLET = "TABLET", "Tablet"

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der GSC-Daten",
    )
    property = models.ForeignKey(
        to=Property,
        verbose_name="Property",
        help_text="Globale ID der GSC-Property",
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
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Letzte Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.date} - {self.property.name}"


class PropertyDataQueryGSC(DataGSC):
    """SEO-Query-Performance der gesamten Property pro Tag, basierend auf Daten der
    Google Search Console."""

    class Meta:
        """Model meta options."""

        db_table = "property_data_query_gsc"
        verbose_name = "Property-Query-Daten (GSC)"
        verbose_name_plural = "Property-Query-Daten (GSC)"
        ordering = ["-date", "-clicks"]
        unique_together = ["date", "property", "query"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der GSC-Daten",
    )
    property = models.ForeignKey(
        to=Property,
        verbose_name="Property",
        help_text="Globale ID der GSC-Property",
        on_delete=models.CASCADE,
        related_name="data_query_gsc",
        related_query_name="data_query_gsc",
    )
    query = models.TextField(
        verbose_name="Query",
        help_text="Query (Suchanfrage)",
    )
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Letzte Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.date} - {self.property.name}"


class PageDataGSC(DataGSC):
    """SEO-Performance pro Tag, basierend auf Daten der Google Search Console."""

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
        help_text="Datum der GSC-Daten",
    )
    page = models.ForeignKey(
        to=Page,
        verbose_name="Seite",
        help_text="Globale ID der Online-Seite",
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
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Letzte Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.date} - {self.page.url}"


class PageDataQueryGSC(DataGSC):
    """SEO-Query-Performance pro Tag pro Seite, basierend auf Daten der Google
    Search Console.
    """

    class Meta:
        """Model meta options."""

        db_table = "page_data_query_gsc"
        verbose_name = "Seiten-Query-Performance (GSC)"
        verbose_name_plural = "Seiten-Query-Performance (GSC)"
        ordering = ["-date", "-clicks"]
        unique_together = ["date", "page", "query"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der GSC-Daten",
    )
    page = models.ForeignKey(
        to=Page,
        verbose_name="Seite",
        help_text="Globale ID der Online-Seite",
        on_delete=models.CASCADE,
        related_name="data_query_gsc",
        related_query_name="data_query_gsc",
    )
    query = models.TextField(
        verbose_name="Query",
        help_text="Query (Suchanfrage)",
    )
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Letzte Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.date} - {self.page.url}"


class PageWebtrekkMeta(models.Model):
    """Meta-Informationen zu einer bestimmten Seite. Es kann mehrere
    Meta-Einträge zur selben Nachrichtenseite geben, wenn z. B. die Überschrift geändert wurde.
    """

    class Meta:
        """Model meta options."""

        db_table = "page_webtrekk_meta"
        verbose_name = "Seiten-Webtrekk-Meta"
        verbose_name_plural = "Seiten-Webtrekk-Metas"
        ordering = ["-created"]
        unique_together = [
            "page",
            "headline",
            "query",
        ]

    page = models.ForeignKey(
        to=Page,
        verbose_name="Seite",
        on_delete=models.CASCADE,
        related_name="webtrekk_metas",
        related_query_name="webtrekk_meta",
        help_text="Die Seite, der die Webtrekk-Meta Informationen zugeordnet wurden",
    )
    headline = models.TextField(
        verbose_name="Titel",
        help_text="Schlagzeile des Nachrichtenartikels",
    )
    query = models.TextField(
        verbose_name="Get-Parameter",
        help_text="Extrahierte Get-Parameter der URL",
    )
    created = models.DateTimeField(
        verbose_name="Zeitpunkt der Erstellung",
        help_text="Der Zeitpunkt, an dem dieser Eintrag in der Datenbank angelegt wurde",
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.headline}"


class PageDataWebtrekk(models.Model):
    """Webtrekk-Performance pro Tag, basierend auf Daten des Webanlysetools Mapp (Webtrekk)."""

    class Meta:
        """Model meta options."""

        db_table = "page_data_webtrekk"
        verbose_name = "Seiten-Daten (Webtrekk)"
        verbose_name_plural = "Seiten-Daten (Webtrekk)"
        ordering = ["-date", "-visits"]
        unique_together = ["date", "webtrekk_meta"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der Webtrekk-Daten",
    )
    webtrekk_meta = models.ForeignKey(
        to=PageWebtrekkMeta,
        verbose_name="Webtrekk-Meta",
        help_text="Globale ID des Webtrekk-Metas",
        on_delete=models.CASCADE,
        related_name="data_webtrekk",
        related_query_name="data_webtrekk",
    )

    visits = models.IntegerField(
        verbose_name="Visits",
        help_text="Visits (pro Tag)",
    )
    visits_search = models.IntegerField(
        verbose_name="Visits via Suchmaschine",
        help_text="Visits via Suchmaschine (pro Tag)",
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        help_text="Impressions (pro Tag)",
    )
    impressions_search = models.IntegerField(
        verbose_name="Impressions via Suchmaschine",
        help_text="Impressions via Suchmaschine (pro Tag)",
    )
    visits_campaign = models.IntegerField(
        verbose_name="Kampagnen-Visits",
        help_text="Kampagnen-Visits (pro Tag)",
    )
    visits_campaign_search = models.IntegerField(
        verbose_name="Kampagnen-Visits via Suchmaschine",
        help_text="Kampagnen-Visits via Suchmaschine (pro Tag)",
    )
    entries = models.IntegerField(
        verbose_name="Einstiege",
        help_text="Einstiege (pro Tag)",
    )
    entries_search = models.IntegerField(
        verbose_name="Einstiege via Suchmaschine",
        help_text="Einstiege via Suchmaschine (pro Tag)",
    )
    exits = models.IntegerField(
        verbose_name="Ausstiege",
        help_text="Ausstiege (pro Tag)",
    )
    exits_search = models.IntegerField(
        verbose_name="Ausstiege via Suchmaschine",
        help_text="Ausstiege via Suchmaschine (pro Tag)",
    )
    bounces = models.IntegerField(
        verbose_name="Bounces",
        help_text="Bounces (pro Tag)",
    )
    bounces_search = models.IntegerField(
        verbose_name="Bounces via Suchmaschine",
        help_text="Bounces via Suchmaschine (pro Tag)",
    )
    length_of_stay = models.DurationField(
        verbose_name="Verweildauer",
        help_text="Verweildauer (pro Tag)",
    )
    length_of_stay_search = models.DurationField(
        verbose_name="Verweildauer via Suchmaschine",
        help_text="Verweildauer via Suchmaschine (pro Tag)",
    )

    def __str__(self):
        return f"{self.date} - {self.webtrekk_meta}"
