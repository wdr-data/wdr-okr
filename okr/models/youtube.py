from django.db import models
from .base import Quintly


class YouTube(Quintly):
    class Meta:
        verbose_name = "YouTube-Account"
        verbose_name_plural = "YouTube-Accounts"


class YouTubeAnalytics(models.Model):
    class Meta:
        verbose_name = "YouTube-Analytics"
        verbose_name_plural = "YouTube-Analytics"
        unique_together = ("youtube", "date", "interval")

    class Interval(models.TextChoices):
        DAILY = "daily", "Täglich"
        WEEKLY = "weekly", "Wöchentlich"
        MONTHLY = "monthly", "Monatlich"

    youtube = models.ForeignKey(
        verbose_name="YouTube-Account",
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="analytic",
        related_query_name="analytics",
    )
    date = models.DateField(verbose_name="Datum")
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
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return (
            f"{self.date}: {self.youtube.name} - {self.Interval(self.interval).label}"
        )


class YouTubeTrafficSource(models.Model):
    class Meta:
        verbose_name = "YouTube-TrafficSource"
        verbose_name_plural = "YouTube-TrafficSources"
        unique_together = ("youtube", "date")

    youtube = models.ForeignKey(
        verbose_name="YouTube-Account",
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="traffic_source",
        related_query_name="traffic_sources",
    )
    date = models.DateField(verbose_name="Datum")
    impressions_home = models.IntegerField(verbose_name="Impressions (Home)")
    impressions_subscriptions = models.IntegerField(verbose_name="Impressions (Abos)")
    impressions_trending = models.IntegerField(verbose_name="Impressions (Trending)")
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.youtube.name}"


class YouTubeAgeRangeDuration(models.Model):
    class Meta:
        verbose_name = "YouTube Age-Range (Viewtime)"
        verbose_name_plural = "YouTube Age-Ranges (Viewtime)"

    age_13_17 = models.DurationField(verbose_name="13 - 17")
    age_18_24 = models.DurationField(verbose_name="18 - 24")
    age_25_34 = models.DurationField(verbose_name="25 - 34")
    age_35_44 = models.DurationField(verbose_name="35 - 44")
    age_45_54 = models.DurationField(verbose_name="45 - 54")
    age_55_64 = models.DurationField(verbose_name="55 - 64")
    age_65_plus = models.DurationField(verbose_name="65+")


class YouTubeAgeRangePercentage(models.Model):
    class Meta:
        verbose_name = "YouTube Age-Range (Prozent)"
        verbose_name_plural = "YouTube Age-Ranges (Prozent)"

    age_13_17 = models.DecimalField(
        verbose_name="13 - 17", max_digits=5, decimal_places=2
    )
    age_18_24 = models.DecimalField(
        verbose_name="18 - 24", max_digits=5, decimal_places=2
    )
    age_25_34 = models.DecimalField(
        verbose_name="25 - 34", max_digits=5, decimal_places=2
    )
    age_35_44 = models.DecimalField(
        verbose_name="35 - 44", max_digits=5, decimal_places=2
    )
    age_45_54 = models.DecimalField(
        verbose_name="45 - 54", max_digits=5, decimal_places=2
    )
    age_55_64 = models.DecimalField(
        verbose_name="55 - 64", max_digits=5, decimal_places=2
    )
    age_65_plus = models.DecimalField(
        verbose_name="65+", max_digits=5, decimal_places=2
    )


class YouTubeViewerAge(models.Model):
    class Meta:
        verbose_name = "YouTube Viewer-Age"
        verbose_name_plural = "YouTube Viewer-Ages"
        unique_together = ("youtube", "date", "interval")

    class Interval(models.TextChoices):
        DAILY = "daily", "Täglich"
        WEEKLY = "weekly", "Wöchentlich"
        MONTHLY = "monthly", "Monatlich"

    youtube = models.ForeignKey(
        verbose_name="YouTube-Account",
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="age_range",
        related_query_name="age_ranges",
    )
    date = models.DateField(verbose_name="Datum")
    interval = models.CharField(
        verbose_name="Zeitraum", choices=Interval.choices, max_length=10
    )

    average_view_duration = models.ForeignKey(
        YouTubeAgeRangeDuration,
        models.CASCADE,
        related_name="+",
        related_query_name="+",
        verbose_name="Durchschnittliche View-Time (absolut)",
    )
    average_percentage_viewed = models.ForeignKey(
        YouTubeAgeRangePercentage,
        models.CASCADE,
        related_name="+",
        related_query_name="+",
        verbose_name="Durchschnittliche View-Time (% des Videos)",
    )
    watch_time = models.ForeignKey(
        YouTubeAgeRangePercentage,
        models.CASCADE,
        related_name="+",
        related_query_name="+",
        verbose_name="Watch-Time (%)",
    )
    views = models.ForeignKey(
        YouTubeAgeRangePercentage,
        models.CASCADE,
        related_name="+",
        related_query_name="+",
        verbose_name="Views (%)",
    )

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return (
            f"{self.date}: {self.youtube.name} - {self.Interval(self.interval).label}"
        )