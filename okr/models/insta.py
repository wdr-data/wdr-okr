from django.db import models
from .base import Product


class Insta(Product):
    class Meta:
        verbose_name = "Instagram-Account"
        verbose_name_plural = "Instagram-Accounts"


class InstaInsights(models.Model):
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
    interval = models.CharField(verbose_name="Zeitraum", choices=Interval.choices, max_length=10)
    reach = models.IntegerField(verbose_name="Reichweite")
    impressions = models.IntegerField(verbose_name="Impressions")
    followers = models.IntegerField(verbose_name="Follower")
    followers_change = models.IntegerField(verbose_name="Veränderung Follower")
    posts_change = models.IntegerField(verbose_name="Veränderung Posts")
    textMessageClicksDay = models.IntegerField(verbose_name="Nachricht senden", null=True)
    emailContactsDay = models.IntegerField(verbose_name="Email senden", null=True)


class InstaPosts(models.Model):
    insta = models.ForeignKey(
        to=Insta,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="post",
    )
    message = models.TextField(verbose_name="Text")
    time = models.DateField(verbose_name="Datum")
    post_type = models.CharField(verbose_name="Typ", max_length=20)
    comments = models.IntegerField(verbose_name="Kommentare")
    likes = models.IntegerField(verbose_name="Likes")
    reach = models.IntegerField(verbose_name="Reichweite")
    impressions = models.IntegerField(verbose_name="Impressions")
    link = models.URLField(verbose_name="Link")


class InstaStories(models.Model):
    insta = models.ForeignKey(
        to=Insta,
        on_delete=models.CASCADE,
        related_name="stories",
        related_query_name="story",
    )
    message = models.CharField(verbose_name="Text", max_length=200)
    time = models.DateField(verbose_name="Datum")
    story_type = models.CharField(verbose_name="Typ", max_length=200)
    comments = models.IntegerField(verbose_name="Kommentare")
    likes = models.IntegerField(verbose_name="Likes")
    reach = models.IntegerField(verbose_name="Reichweite")
    impressions = models.IntegerField(verbose_name="Impressions")

class Collaborations(models.Model):
    insta = models.ForeignKey(
        to=Insta,
        on_delete=models.CASCADE,
        related_name="collaborations",
        related_query_name="collaboration",
    )
    time = models.DateField(verbose_name="Datum")
    influencer= models.CharField(verbose_name="Influencer:in", max_length=100)
    followers = models.IntegerField(verbose_name="Follower")
    description = models.TextField(verbose_name="Beschreibung")
