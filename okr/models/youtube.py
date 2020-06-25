from django.db import models
from .base import Product


class YouTube(Product):
    class Meta:
        verbose_name = "YouTube-Account"
        verbose_name_plural = "YouTube-Accounts"


class YouTubeAnalytics(models.Model):
    class Meta:
        verbose_name = "YouTube-Analytic"
        verbose_name_plural = "YouTube-Analytics"
        unique_together = ("youtube", "time", "interval")

    class Interval(models.TextChoices):
        DAILY = "daily", "Täglich"
        WEEKLY = "weekly", "Wöchentlich"
        MONTHLY = "monthly", "Monatlich"

    youtube = models.ForeignKey(
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="analytic",
        related_query_name="analytics",
    )
    time = models.DateField(verbose_name="Datum")
    interval = models.CharField(
        verbose_name="Zeitraum", choices=Interval.choices, max_length=10
    )

    views = models.IntegerField(verbose_name="Views", null=True)
    likes = models.IntegerField(verbose_name="Likes", null=True)
    dislikes = models.IntegerField(verbose_name="Dislikes", null=True)
    estimated_minutes_watched = models.IntegerField(
        verbose_name="Gesehene Minuten (geschätzt)", null=True
    )
    average_view_duration = models.IntegerField(
        verbose_name="Sehdauer im Schnitt", null=True
    )

    def __str__(self):
        return (
            f"{self.time}: {self.youtube.name} - {self.Interval(self.interval).label}"
        )

class YouTubeTrafficSource(models.Model):
    class Meta:
        verbose_name = "YouTube-TrafficSource"
        verbose_name_plural = "YouTube-TrafficSources"
