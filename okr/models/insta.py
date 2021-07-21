"""Database models for Instagram."""

from django.db import models
from .base import Quintly


class Insta(Quintly):
    """Instagram-Accounts, basierend auf Daten von Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "instagram"
        verbose_name = "Instagram-Account"
        verbose_name_plural = "Instagram-Accounts"
        ordering = Quintly.Meta.ordering


class InstaInsight(models.Model):
    """Performance-Daten einzelner Instagram-Accounts, basierend auf Daten von Instagram
    Insights.
    """

    class Meta:
        """Model meta options."""

        db_table = "instagram_insights"
        verbose_name = "Instagram-Insight"
        verbose_name_plural = "Instagram-Insights"
        unique_together = ("insta", "date", "interval")
        ordering = ["-date"]

    class Interval(models.TextChoices):
        """Available update intervals."""

        DAILY = "daily", "Täglich"
        WEEKLY = "weekly", "Wöchentlich"
        MONTHLY = "monthly", "Monatlich"

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
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
    reach = models.IntegerField(verbose_name="Reichweite", null=True)
    impressions = models.IntegerField(verbose_name="Impressions", null=True)
    followers = models.IntegerField(verbose_name="Follower")
    followers_change = models.IntegerField(verbose_name="Veränderung Follower")
    posts_change = models.IntegerField(verbose_name="Veränderung Posts")
    text_message_clicks_day = models.IntegerField(
        verbose_name="Nachricht senden", null=True
    )
    email_contacts_day = models.IntegerField(verbose_name="Email senden", null=True)
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.insta.name} - {self.Interval(self.interval).label}"


class InstaPost(models.Model):
    """Grundlegende Daten zu einzelnen Instagram-Postings."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_post"
        verbose_name = "Instagram-Post"
        verbose_name_plural = "Instagram-Posts"
        ordering = ["-created_at"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="post",
    )
    external_id = models.CharField(
        verbose_name="Externe ID", max_length=25, unique=True
    )
    message = models.TextField(verbose_name="Text", help_text="Volltext des Postings")
    created_at = models.DateTimeField(verbose_name="Erstellungsdatum")
    post_type = models.CharField(
        verbose_name="Typ",
        help_text="Art des Postings (Image, Carousel, etc)",
        max_length=20,
    )
    comments = models.IntegerField(
        verbose_name="Kommentare",
        help_text="Anzahl der Kommentare",
        null=True,
    )
    likes = models.IntegerField(
        verbose_name="Likes",
        help_text="Anzahl der Likes",
        null=True,
    )
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        null=True,
    )
    saved = models.IntegerField(
        verbose_name="Saves",
        help_text="Anzahl der Saves",
        null=True,
    )
    video_views = models.IntegerField(
        verbose_name="Video-Views",
        help_text="Video-Views (3 sec oder mehr)",
        null=True,
    )
    link = models.URLField(verbose_name="Link", help_text="URL des Postings")
    quintly_import_time = models.DateTimeField(
        verbose_name="Import Time",
        help_text="Stand der Daten bei Quintly",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.insta.name} - {self.post_type}"


class InstaStory(models.Model):
    """Daten zu einzelnen Instagram Stories.

    Jede Zeile der Datenbank entählt Daten zu einem Story-Element. Eine Insta-Story
    besteht in der Regel aus mehreren Story-Elementen.
    """

    class Meta:
        """Model meta options."""

        db_table = "instagram_story"
        verbose_name = "Instagram-Story"
        verbose_name_plural = "Instagram-Stories"
        ordering = ["-created_at"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="stories",
        related_query_name="story",
    )
    external_id = models.CharField(
        verbose_name="Externe ID",
        max_length=25,
        unique=True,
    )
    caption = models.TextField(
        verbose_name="Text",
        help_text="Volltext des Story-Elements",
        null=True,
    )
    created_at = models.DateTimeField(verbose_name="Erstellungszeitpunkt")
    story_type = models.CharField(
        verbose_name="Typ",
        help_text="Art des Story-Elements (Image/Video)",
        max_length=200,
    )
    replies = models.IntegerField(
        verbose_name="Antworten",
        help_text="Anzahl der Antworten",
        null=True,
    )
    exits = models.IntegerField(
        verbose_name="Exits",
        help_text="Anzahl der Ausstiege",
        null=True,
    )
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        null=True,
    )
    taps_forward = models.IntegerField(
        verbose_name="Taps forward",
        help_text="Anzahl der forward Taps",
        null=True,
    )
    taps_back = models.IntegerField(
        verbose_name="Taps back",
        help_text="Anzahl der back Taps",
        null=True,
    )
    link = models.URLField(
        verbose_name="Link",
        help_text="URL des Story-Elements",
        max_length=1024,
    )
    quintly_import_time = models.DateTimeField(
        verbose_name="Import Time",
        help_text="Stand der Daten bei Quintly",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.insta.name} - {self.story_type}"


class InstaIGTV(models.Model):
    """Grundlegende Daten zu einzelnen Instagram IGTV Videos."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_tv_video"
        verbose_name = "Instagram IGTV Video"
        verbose_name_plural = "Instagram IGTV Videos"
        ordering = ["-created_at"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="igtv_videos",
        related_query_name="igtv_video",
    )
    external_id = models.CharField(
        verbose_name="Externe ID", max_length=25, unique=True
    )
    created_at = models.DateTimeField(verbose_name="Erstellungsdatum")
    message = models.TextField(
        verbose_name="Text",
        help_text="Beschreibungstext des IGTV Videos",
    )
    video_title = models.TextField(
        verbose_name="Titel",
        help_text="Titel des IGTV Videos",
    )
    likes = models.IntegerField(
        verbose_name="Likes",
        help_text="Anzahl der Likes",
        null=True,
    )
    comments = models.IntegerField(
        verbose_name="Kommentare",
        help_text="Anzahl der Kommentare",
        null=True,
    )
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        null=True,
    )
    saved = models.IntegerField(
        verbose_name="Saves",
        help_text="Anzahl der Saves",
        null=True,
    )
    video_views = models.IntegerField(
        verbose_name="Likes",
        help_text="Video-Views (3 sec oder mehr)",
        null=True,
    )
    link = models.URLField(verbose_name="Link", help_text="URL des Postings")
    quintly_import_time = models.DateTimeField(
        verbose_name="Import Time",
        help_text="Stand der Daten bei Quintly",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.insta.name} - {self.video_title}"
