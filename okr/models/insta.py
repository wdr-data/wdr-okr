"""  Database models for instagram.
"""

from django.db import models
from .base import Quintly


class Insta(Quintly):
    """ Instagram accounts, based on data from Quintly.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "instagram"
        verbose_name = "Instagram-Account"
        verbose_name_plural = "Instagram-Accounts"
        ordering = Quintly.Meta.ordering


class InstaInsight(models.Model):
    """ Performance data of Instagram accounts, based on data from Instagram Insights.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "instagram_insights"
        verbose_name = "Instagram-Insight"
        verbose_name_plural = "Instagram-Insights"
        unique_together = ("insta", "date", "interval")
        ordering = ["-date"]

    class Interval(models.TextChoices):
        """ Available update intervals.
        """

        DAILY = "daily", "Täglich"
        WEEKLY = "weekly", "Wöchentlich"
        MONTHLY = "monthly", "Monatlich"

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="insights",
        related_query_name="insight",
    )
    date = models.DateField(verbose_name="Datum")
    interval = models.CharField(
        verbose_name="Zeitraum", choices=Interval.choices, max_length=10
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
    """ Data on individual Instagram posts.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "instagram_post"
        verbose_name = "Instagram-Post"
        verbose_name_plural = "Instagram-Posts"
        ordering = ["-created_at"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="post",
    )
    external_id = models.CharField(verbose_name="ID", max_length=25, unique=True)
    message = models.TextField(verbose_name="Text")
    created_at = models.DateTimeField(verbose_name="Erstellt")
    post_type = models.CharField(verbose_name="Typ", max_length=20)
    comments = models.IntegerField(verbose_name="Kommentare")
    likes = models.IntegerField(verbose_name="Likes")
    reach = models.IntegerField(verbose_name="Reichweite")
    impressions = models.IntegerField(verbose_name="Impressions")
    link = models.URLField(verbose_name="Link")
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.insta.name} - {self.post_type}"


class InstaStory(models.Model):
    """ Data on individual Instagram stories.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "instagram_story"
        verbose_name = "Instagram-Story"
        verbose_name_plural = "Instagram-Stories"
        ordering = ["-created_at"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="stories",
        related_query_name="story",
    )
    external_id = models.CharField(verbose_name="ID", max_length=25, unique=True)
    caption = models.TextField(verbose_name="Text", null=True)
    created_at = models.DateTimeField(verbose_name="Erstellt")
    story_type = models.CharField(verbose_name="Typ", max_length=200)
    replies = models.IntegerField(verbose_name="Antworten")
    exits = models.IntegerField(verbose_name="Exits")
    reach = models.IntegerField(verbose_name="Reichweite")
    impressions = models.IntegerField(verbose_name="Impressions")
    link = models.URLField(verbose_name="Link", max_length=1024)
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.insta.name} - {self.story_type}"


class InstaCollaborationType(models.Model):
    """ Data on Instagram collaboration types.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "instagram_collaboration_type"
        verbose_name = "Instagram-Collaboration Format"
        verbose_name_plural = "Instagram-Collaboration Formate"
        ordering = ["name"]

    name = models.CharField("Name", max_length=200, null=False, blank=False)

    def __str__(self):
        return self.name


class InstaCollaboration(models.Model):
    """ Data on Instagram collaborations.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "instagram_collaboration"
        verbose_name = "Instagram-Collaboration"
        verbose_name_plural = "Instagram-Collaborations"
        ordering = ["-date"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="collaborations",
        related_query_name="collaboration",
    )
    date = models.DateField(verbose_name="Datum")
    influencer = models.CharField(
        verbose_name="Influencer*in (Account-Name)", max_length=100
    )
    followers = models.IntegerField(
        verbose_name="Follower", help_text="Anzahl Follower der Influencer*in"
    )
    collaboration_type = models.ForeignKey(
        InstaCollaborationType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="collaboration",
        verbose_name="Format",
    )
    topic = models.TextField(verbose_name="Thema", help_text="Thema der Kollaboration")
    description = models.TextField(verbose_name="Notiz", blank=True)
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.insta.name} - {self.influencer}"
