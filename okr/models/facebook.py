"""Database models for Facebook."""

from django.db import models
from .base import Quintly


class Facebook(Quintly):
    """Facebook-Accounts, basierend auf Daten von Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "facebook"
        verbose_name = "Facebook-Account"
        verbose_name_plural = "Facebook-Accounts"
        ordering = Quintly.Meta.ordering


class FacebookInsight(models.Model):
    """Performance-Daten einzelner Facebook-Accounts, basierend auf Daten von Facebook
    Insights.
    """

    class Meta:
        """Model meta options."""

        db_table = "facebook_insights"
        verbose_name = "Facebook-Insight"
        verbose_name_plural = "Facebook-Insights"
        unique_together = ("facebook", "date", "interval")
        ordering = ["-date"]

    class Interval(models.TextChoices):
        """Available update intervals."""

        DAILY = "daily", "Täglich"
        WEEKLY = "weekly", "Wöchentlich"
        MONTHLY = "monthly", "Monatlich"

    facebook = models.ForeignKey(
        verbose_name="Facebook-Account",
        help_text="Globale ID des Facebook-Accounts",
        to=Facebook,
        on_delete=models.CASCADE,
        related_name="insights",
        related_query_name="insight",
    )
    date = models.DateField(verbose_name="Datum")
    interval = models.CharField(
        verbose_name="Zeitraum",
        help_text="Intervall (täglich, wöchentlich oder monatlich)",
        choices=Interval.choices,
        max_length=10,
    )

    fans = models.IntegerField(verbose_name="Fans")
    follows = models.IntegerField(verbose_name="Follower")
    impressions_unique = models.IntegerField(verbose_name="Impressions (Unique)")
    fans_online_per_day = models.IntegerField(
        verbose_name="Fans online pro Tag",
        null=True,
    )

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return (
            f"{self.date}: {self.facebook.name} - {self.Interval(self.interval).label}"
        )


class FacebookPost(models.Model):
    """Grundlegende Daten zu einzelnen Facebook-Postings."""

    class Meta:
        """Model meta options."""

        db_table = "facebook_post"
        verbose_name = "Facebook-Post"
        verbose_name_plural = "Facebook-Posts"
        ordering = ["-created_at"]

    facebook = models.ForeignKey(
        verbose_name="Facebook-Account",
        help_text="Globale ID des Facebook-Accounts",
        to=Facebook,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="post",
    )
    created_at = models.DateTimeField(verbose_name="Erstellungsdatum")

    post_type = models.CharField(
        verbose_name="Typ",
        help_text="Art des Postings",
        max_length=20,
    )
    external_id = models.CharField(
        verbose_name="Externe ID", max_length=64, unique=True
    )
    link = models.URLField(verbose_name="Link", help_text="URL des Postings")
    message = models.TextField(
        verbose_name="Text",
        help_text="Volltext des Postings",
        null=True,
    )

    likes = models.IntegerField(
        verbose_name="Likes 👍",
        help_text="Anzahl der Likes",
    )
    love = models.IntegerField(
        verbose_name="Love ❤️",
        help_text="Anzahl der Love-Reaktionen",
    )
    wow = models.IntegerField(
        verbose_name="WOW 😯",
        help_text="Anzahl der WOW-Reaktionen",
    )
    haha = models.IntegerField(
        verbose_name="Haha 😂",
        help_text="Anzahl der Haha-Reaktionen",
    )
    sad = models.IntegerField(
        verbose_name="Traurig 😢",
        help_text="Anzahl der Traurig-Reaktionen",
    )
    angry = models.IntegerField(
        verbose_name="Wütend 😡",
        help_text="Anzahl der Wütend-Reaktionen",
    )

    comments = models.IntegerField(
        verbose_name="Kommentare", help_text="Anzahl der Kommentare"
    )
    shares = models.IntegerField(verbose_name="Shares", help_text="Anzahl der Shares")
    impressions_unique = models.IntegerField(verbose_name="Impressions (Unique)")

    is_published = models.BooleanField(verbose_name="Veröffentlicht")
    is_hidden = models.BooleanField(verbose_name="Versteckt")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.facebook.name} - {self.post_type}"
