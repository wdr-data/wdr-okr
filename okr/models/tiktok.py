"""Database models for TikTok."""

from django.db import models
from .base import Quintly


class TikTok(Quintly):
    """TikTok-Accounts, basierend auf Daten von Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "tiktok"
        verbose_name = "TikTok-Account"
        verbose_name_plural = "TikTok-Accounts"
        ordering = Quintly.Meta.ordering


class TikTokData(models.Model):
    """Performance-Daten einzelner TikTok-Accounts, basierend auf öffentlichen
    TikTok-Daten von Quintly.
    """

    class Meta:
        """Model meta options."""

        db_table = "tiktok_data"
        verbose_name = "TikTok-Daten"
        verbose_name_plural = "TikTok-Daten"
        unique_together = ("tiktok", "date")
        ordering = ["-date"]

    tiktok = models.ForeignKey(
        verbose_name="TikTok-Account",
        help_text="Globale ID des TikTok-Accounts",
        to=TikTok,
        on_delete=models.CASCADE,
        related_name="data",
        related_query_name="data",
    )

    date = models.DateField(verbose_name="Datum")

    followers = models.IntegerField(
        verbose_name="Follower",
        help_text="Followers des Accounts",
        null=True,
    )
    followers_change = models.IntegerField(
        verbose_name="Veränderung Followers",
        help_text="Veränderung Followers",
        null=True,
    )
    following = models.IntegerField(
        verbose_name="Following",
        help_text="Gefolgte Accounts",
        null=True,
    )
    following_change = models.IntegerField(
        verbose_name="Veränderung Following",
        help_text="Veränderung der gefolgten Accounts",
        null=True,
    )
    likes = models.IntegerField(
        verbose_name="Likes",
        help_text="Likes für den Account",
        null=True,
    )
    likes_change = models.IntegerField(
        verbose_name="Veränderung Likes",
        help_text="Veränderung der Likes für den Account",
        null=True,
    )
    videos = models.IntegerField(
        verbose_name="Videos",
        help_text="Anzahl der Videos des Accounts",
        null=True,
    )
    videos_change = models.IntegerField(
        verbose_name="Veränderung Videos",
        help_text="Veränderung der Anzahl der Videos des Accounts",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.tiktok.name}"


class TikTokHashtag(models.Model):
    """Hashtags für TikTok-Posts."""

    class Meta:
        """Model meta options."""

        db_table = "tiktok_hashtag"
        verbose_name = "TikTok-Hashtag"
        verbose_name_plural = "TikTok-Hashtags"
        ordering = ["hashtag"]

    hashtag = models.TextField(
        verbose_name="Hashtag",
        unique=True,
    )

    first_seen = models.DateTimeField(
        verbose_name="Zeitpunkt der Ersterfassung",
        help_text="Der Zeitpunkt, zu dem dieser Hashtag erstmals erfasst wurde.",
        auto_now_add=True,
    )

    def __str__(self):
        return self.hashtag


class TikTokChallenge(models.Model):
    """Challenges für TikTok-Posts."""

    class Meta:
        """Model meta options."""

        db_table = "tiktok_challenge"
        verbose_name = "TikTok-Challenge"
        verbose_name_plural = "TikTok-Challenges"
        ordering = ["title"]

    title = models.TextField(
        verbose_name="Title",
        help_text="Title der Challenge",
        unique=True,
    )

    description = models.TextField(
        verbose_name="Description",
        help_text="Description der Challenge",
        blank=True,
    )

    first_seen = models.DateTimeField(
        verbose_name="Zeitpunkt der Ersterfassung",
        help_text="Der Zeitpunkt, zu dem diese Challenge erstmals erfasst wurde.",
        auto_now_add=True,
    )

    def __str__(self):
        return self.title


class TikTokTag(models.Model):
    """Tags für TikTok-Posts."""

    class Meta:
        """Model meta options."""

        db_table = "tiktok_tag"
        verbose_name = "TikTok-Tag"
        verbose_name_plural = "TikTok-Tags"
        ordering = ["name"]

    name = models.TextField(
        verbose_name="Title",
        help_text="Title der Challenge",
        unique=True,
    )

    first_seen = models.DateTimeField(
        verbose_name="Zeitpunkt der Ersterfassung",
        help_text="Der Zeitpunkt, zu dem dieser Tag erstmals erfasst wurde.",
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class TikTokPost(models.Model):
    """Grundlegende Daten zu einzelnen TikTok-Postings."""

    class Meta:
        """Model meta options."""

        db_table = "tiktok_post"
        verbose_name = "TikTok-Post"
        verbose_name_plural = "TikTok-Posts"
        ordering = ["-created_at"]

    tiktok = models.ForeignKey(
        verbose_name="TikTok-Account",
        help_text="Globale ID des TikTok-Accounts",
        to=TikTok,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="post",
    )

    external_id = models.TextField(verbose_name="Externe ID", unique=True)
    created_at = models.DateTimeField(verbose_name="Erstellungsdatum")
    link = models.URLField(verbose_name="Link", help_text="URL des Postings.")

    description = models.TextField(
        verbose_name="Text", help_text="Volltext des Postings."
    )

    hashtags = models.ManyToManyField(
        to=TikTokHashtag,
        verbose_name="Hashtags",
        db_table="tiktok_post_tiktok_hashtag",
        related_name="posts",
        related_query_name="post",
        help_text="Die für den TikTok-Post vergebenen Hashtags.",
        blank=True,
    )

    challenges = models.ManyToManyField(
        to=TikTokChallenge,
        verbose_name="Challenges",
        db_table="tiktok_post_tiktok_challenge",
        related_name="posts",
        related_query_name="post",
        help_text="Die für den TikTok-Post verwendeten Challenges.",
        blank=True,
    )

    tags = models.ManyToManyField(
        to=TikTokTag,
        verbose_name="Tags",
        db_table="tiktok_post_tiktok_tag",
        related_name="posts",
        related_query_name="post",
        help_text="Die für den TikTok-Post verwendeten Tags.",
        blank=True,
    )

    video_length = models.DurationField(
        verbose_name="Video Länge",
        help_text="Länge des Videos in Sekunden.",
        null=True,
    )

    video_cover_url = models.URLField(
        verbose_name="Video-Cover URL",
        help_text="URL des Video-Coverbildes.",
        null=True,
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

    shares = models.IntegerField(
        verbose_name="Shares",
        help_text="Anzahl der Shares",
        null=True,
    )

    views = models.IntegerField(
        verbose_name="Views",
        help_text="Anzahl der Views",
        null=True,
    )

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.tiktok.name}"
