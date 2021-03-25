"""Database models for custom key results."""

import datetime as dt

from django.db import models


class CustomKeyResult(models.Model):
    class ProductType(models.TextChoices):
        ABTEILUNG = "abteilung", "Abteilung"
        ALLGEMEIN = "allgemein", "Allgemein"
        APP = "app", "App"
        CLUBHOUSE = "clubhouse", "Clubhouse"
        FACEBOOK = "facebook", "Facebook"
        FLASH_BRIEFING = "flash_briefing", "Flash-Briefing"
        HAUPTABTEILUNG = "hauptabteilung", "Hauptabteilung"
        HOERFUNK_SENDUNG = "hoerfunk_sendung", "Hörfunk-Sendung"
        INSTAGRAM = "instagram", "Instagram"
        MESSENGER = "messenger", "Messenger"
        ONLINE = "online", "Online"
        PODCAST = "podcast", "Podcast"
        SKILL = "skill", "Skill"
        SNAPCHAT = "snapchat", "Snapchat"
        SONSTIGES = "sonstiges", "Sonstiges"
        TEAM = "team", "Team"
        TIKTOK = "tiktok", "TikTok"
        TV_SENDUNG = "tv_sendung", "TV-Sendung"
        TWITTER = "twitter", "Twitter"
        VIDEOTEXT = "videotext", "Videotext"
        YOUTUBE = "youtube", "YouTube"
        ZULIEFERUNG = "zulieferung", "Zulieferung"

    class KeyResultType(models.TextChoices):
        TEXT = "text", "Text"
        INTEGER = "integer", "Zahl"

    class Meta:
        """Model meta options."""

        db_table = "custom_key_result"
        verbose_name = "Manuelle Kennzahl-Definition"
        verbose_name_plural = "Manuelle Kennzahl-Definitionen"
        ordering = ["product_type", "product_name"]

    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        verbose_name="Produkt-Typ",
        help_text="Produkt-Typ für die Kennzahl.",
    )

    product_name = models.TextField(
        verbose_name="Produkt-Name",
        help_text="Produkt-Name (Beispiel: 0630 by WDR aktuell).",
    )

    key_result = models.TextField(
        verbose_name="Kennzahl",
        help_text="Kennzahl (Beispiel: Anzahl Nachrichten pro Woche).",
    )

    description = models.TextField(
        verbose_name="Beschreibung",
        blank=True,
    )

    key_result_type = models.CharField(
        max_length=10,
        choices=KeyResultType.choices,
        verbose_name="Kennzahlen-Typ",
        help_text="Art der Kennzahl.",
    )

    def __str__(self):
        return f"{self.ProductType(self.product_type).label} - {self.product_name} - {self.key_result}"


class CustomKeyResultRecord(models.Model):
    class Meta:
        """Model meta options."""

        db_table = "custom_key_result_record"
        verbose_name = "Manuelle Kennzahl"
        verbose_name_plural = "Manuelle Kennzahlen"
        ordering = ["-date", "key_result"]
        unique_together = ["key_result", "date"]

    key_result = models.ForeignKey(
        verbose_name="Kennzahl",
        to=CustomKeyResult,
        on_delete=models.CASCADE,
        related_name="records",
        related_query_name="record",
        help_text="Bezeichnung der manuell angelegten Kennzahl.",
    )

    date = models.DateField(
        verbose_name="Datum des Eintrags",
        help_text="Datum des manuellen Daten-Eintrags.",
    )

    value_integer = models.IntegerField(
        verbose_name="Wert",
        null=True,
    )

    value_text = models.TextField(
        verbose_name="Wert",
        null=True,
    )

    note = models.TextField(
        verbose_name="Notiz",
        blank=True,
    )

    def __str__(self):
        return f'{self.key_result} ({dt.datetime.strftime(self.date, "%d.%m.%Y")})'
