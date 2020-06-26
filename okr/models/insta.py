from django.db import models
from .base import Product


class Insta(Product):
    class Meta:
        verbose_name = "Instagram-Account"
        verbose_name_plural = "Instagram-Accounts"


class InstaInsight(models.Model):
    class Meta:
        verbose_name = "Instagram-Insight"
        verbose_name_plural = "Instagram-Insights"
        unique_together = ("insta", "time", "interval")

    class Interval(models.TextChoices):
        DAILY = "daily", "Täglich"
        WEEKLY = "weekly", "Wöchentlich"
        MONTHLY = "monthly", "Monatlich"

    insta = models.ForeignKey(
        to=Insta,
        on_delete=models.CASCADE,
        related_name="insights",
        related_query_name="insight",
    )
    time = models.DateField(verbose_name="Datum")
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
        return f"{self.time}: {self.insta.name} - {self.Interval(self.interval).label}"


class InstaPost(models.Model):
    class Meta:
        verbose_name = "Instagram-Post"
        verbose_name_plural = "Instagram-Posts"

    insta = models.ForeignKey(
        to=Insta,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="post",
    )
    external_id = models.CharField(verbose_name="ID", max_length=25, unique=True)
    message = models.TextField(verbose_name="Text")
    time = models.DateTimeField(verbose_name="Erstellt")
    post_type = models.CharField(verbose_name="Typ", max_length=20)
    comments = models.IntegerField(verbose_name="Kommentare")
    likes = models.IntegerField(verbose_name="Likes")
    reach = models.IntegerField(verbose_name="Reichweite")
    impressions = models.IntegerField(verbose_name="Impressions")
    link = models.URLField(verbose_name="Link")
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.time}: {self.insta.name} - {self.post_type}"


class InstaStory(models.Model):
    class Meta:
        verbose_name = "Instagram-Story"
        verbose_name_plural = "Instagram-Stories"

    insta = models.ForeignKey(
        to=Insta,
        on_delete=models.CASCADE,
        related_name="stories",
        related_query_name="story",
    )
    external_id = models.CharField(verbose_name="ID", max_length=25, unique=True)
    caption = models.TextField(verbose_name="Text", null=True)
    time = models.DateTimeField(verbose_name="Erstellt")
    story_type = models.CharField(verbose_name="Typ", max_length=200)
    replies = models.IntegerField(verbose_name="Antworten")
    exits = models.IntegerField(verbose_name="Exits")
    reach = models.IntegerField(verbose_name="Reichweite")
    impressions = models.IntegerField(verbose_name="Impressions")
    link = models.URLField(verbose_name="Link", max_length=1024)
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.time}: {self.insta.name} - {self.story_type}"


class InstaCollaborationType(models.Model):
    class Meta:
        verbose_name = "Instagram-Collaboration Format"
        verbose_name_plural = "Instagram-Collaboration Formate"

    name = models.CharField("Name", max_length=200, null=False, blank=False)

    def __str__(self):
        return self.name


class InstaCollaboration(models.Model):
    class Meta:
        verbose_name = "Instagram-Collaboration"
        verbose_name_plural = "Instagram-Collaborations"

    insta = models.ForeignKey(
        to=Insta,
        on_delete=models.CASCADE,
        related_name="collaborations",
        related_query_name="collaboration",
    )
    time = models.DateField(verbose_name="Datum")
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
        return f"{self.time}: {self.insta.name} - {self.influencer}"
