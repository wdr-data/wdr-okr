"""Database models for cached requests.
Contains results of API queries that can be used to reduce the number of new API
queries.
"""

from django.db import models


class CachedWebtrekkRequest(models.Model):
    """Archiv für zurückliegende Webtrekk Abfragen um übermäßige Anfragen an die
    API zu verhindern.
    """

    class Meta:
        """Model meta options."""

        db_table = "cached_webtrekk_request"
        verbose_name = "Webtrekk Cache-Eintrag"
        verbose_name_plural = "Webtrekk Cache-Einträge"
        ordering = ["last_updated"]

    payload = models.TextField(
        verbose_name="Webtrekk Query-Payload",
        help_text="Query-Payload für Archiv-Eintrag",
        unique=True,
    )

    response = models.TextField(
        verbose_name="Webtrekk Response",
        help_text="API-Response von Webtrekk",
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Jüngste Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return self.last_updated
