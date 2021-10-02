"""Database models for Twitter."""

from django.db import models
from .base import Quintly


class Twitter(Quintly):
    """Twitter-Accounts, basierend auf Daten von Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "twitter"
        verbose_name = "Twitter-Account"
        verbose_name_plural = "Twitter-Accounts"
        ordering = Quintly.Meta.ordering


class TwitterInsight(models.Model):
    """Performance-Daten einzelner Twitter-Accounts, basierend auf Daten von Twitter
    Insights.
    """

    class Meta:
        """Model meta options."""

        db_table = "twitter_insights"
        verbose_name = "Twitter-Insight"
        verbose_name_plural = "Twitter-Insights"
        unique_together = ("twitter", "date")
        ordering = ["-date"]

    twitter = models.ForeignKey(
        verbose_name="Twitter-Account",
        help_text="Globale ID des Twitter-Accounts",
        to=Twitter,
        on_delete=models.CASCADE,
        related_name="insights",
        related_query_name="insight",
    )
    date = models.DateField(verbose_name="Datum")

    followers = models.IntegerField(verbose_name="Follower")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.twitter.name}"


class Tweet(models.Model):
    """Grundlegende Daten zu einzelnen Tweets."""

    class Meta:
        """Model meta options."""

        db_table = "tweet"
        verbose_name = "Tweet"
        verbose_name_plural = "Tweets"
        ordering = ["-created_at"]

    twitter = models.ForeignKey(
        verbose_name="Twitter-Account",
        help_text="Globale ID des Twitter-Accounts",
        to=Twitter,
        on_delete=models.CASCADE,
        related_name="tweets",
        related_query_name="tweet",
    )
    created_at = models.DateTimeField(verbose_name="Erstellungsdatum")

    tweet_type = models.CharField(
        verbose_name="Typ",
        help_text="Art des Tweets",
        max_length=20,
        null=True,
    )
    external_id = models.CharField(
        verbose_name="Externe ID", max_length=64, unique=True
    )
    link = models.URLField(verbose_name="Link", help_text="URL des Postings")
    is_retweet = models.BooleanField(verbose_name="Retweet")
    message = models.TextField(
        verbose_name="Text",
        help_text="Volltext des Tweets",
        null=True,
    )

    favs = models.IntegerField(
        verbose_name="Favorites",
        help_text="Anzahl der Favorites",
    )
    retweets = models.IntegerField(
        verbose_name="Retweets",
        help_text="Anzahl der Retweets",
    )
    replies = models.IntegerField(
        verbose_name="Antworten",
        help_text="Anzahl der Antworten",
    )

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.twitter.name} - {self.tweet_type}"
