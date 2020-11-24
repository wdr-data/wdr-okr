"""Database models for YouTube."""

from django.db import models
from .base import Quintly


class YouTube(Quintly):
    """Youtube accounts, based on data from Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "youtube"
        verbose_name = "YouTube-Account"
        verbose_name_plural = "YouTube-Accounts"
        ordering = Quintly.Meta.ordering


class YouTubeAnalytics(models.Model):
    """Performance data of YouTube accounts, based on data from YouTube analytics."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_analytics"
        verbose_name = "YouTube-Analytics"
        verbose_name_plural = "YouTube-Analytics"
        unique_together = ("youtube", "date", "interval")
        ordering = ["-date"]

    class Interval(models.TextChoices):
        """Available update intervals."""

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
    """Performance data of YouTube accounts, based on YouTube traffic source data."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_traffic_source"
        verbose_name = "YouTube-TrafficSource"
        verbose_name_plural = "YouTube-TrafficSources"
        unique_together = ("youtube", "date")
        ordering = ["-date"]

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


class YouTubeAgeRangeBase(models.Model):
    """Base class for demographics data of YouTube accounts."""

    class Meta:
        """Model meta options."""

        abstract = True
        unique_together = ("youtube", "date", "interval")
        ordering = ["-date"]

    class Interval(models.TextChoices):
        """Available update intervals."""

        DAILY = "daily", "Täglich"
        WEEKLY = "weekly", "Wöchentlich"
        MONTHLY = "monthly", "Monatlich"

    youtube = models.ForeignKey(
        verbose_name="YouTube-Account",
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="+",
        related_query_name="+",
    )
    date = models.DateField(verbose_name="Datum")
    interval = models.CharField(
        verbose_name="Zeitraum", choices=Interval.choices, max_length=10
    )

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return (
            f"{self.youtube.name}: {self.date} ({self.Interval(self.interval).label})"
        )


class YouTubeAgeRangeDuration(YouTubeAgeRangeBase):
    """Demographics data of YouTube accounts, based on YouTube age range duration data."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_age_range_duration"
        abstract = True
        unique_together = YouTubeAgeRangeBase.Meta.unique_together
        ordering = YouTubeAgeRangeBase.Meta.ordering

    age_13_17 = models.DurationField(verbose_name="13 - 17")
    age_18_24 = models.DurationField(verbose_name="18 - 24")
    age_25_34 = models.DurationField(verbose_name="25 - 34")
    age_35_44 = models.DurationField(verbose_name="35 - 44")
    age_45_54 = models.DurationField(verbose_name="45 - 54")
    age_55_64 = models.DurationField(verbose_name="55 - 64")
    age_65_plus = models.DurationField(verbose_name="65+")


class YouTubeAgeRangePercentage(YouTubeAgeRangeBase):
    """Demographics data of YouTube accounts, based on YouTube age range percentage data."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_age_range_percentage"
        abstract = True
        unique_together = YouTubeAgeRangeBase.Meta.unique_together
        ordering = YouTubeAgeRangeBase.Meta.ordering

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


class YouTubeAgeRangeAverageViewDuration(YouTubeAgeRangeDuration):
    """Demographics data of YouTube accounts, based on YouTube age range average
    view duration data.
    """

    class Meta:
        """Model meta options."""

        db_table = "youtube_age_range_average_view_duration"
        verbose_name = "YouTube Age-Range (Average View Duration)"
        verbose_name_plural = "YouTube Age-Ranges (Average View Duration)"
        unique_together = YouTubeAgeRangeDuration.Meta.unique_together
        ordering = YouTubeAgeRangeDuration.Meta.ordering


class YouTubeAgeRangeAverageViewPercentage(YouTubeAgeRangePercentage):
    """Demographics data of YouTube accounts, based on YouTube age range average view
    percentage data.
    """

    class Meta:
        """Model meta options."""

        db_table = "youtube_age_range_average_view_percentage"
        verbose_name = "YouTube Age-Range (Average Percentage Viewed)"
        verbose_name_plural = "YouTube Age-Ranges (Average Percentage Viewed)"
        unique_together = YouTubeAgeRangePercentage.Meta.unique_together
        ordering = YouTubeAgeRangePercentage.Meta.ordering


class YouTubeAgeRangeWatchTimePercentage(YouTubeAgeRangePercentage):
    """Demographics data of YouTube accounts, based on YouTube age range watch time
    percentage data.
    """

    class Meta:
        """Model meta options."""

        db_table = "youtube_age_range_watch_time_percentage"
        verbose_name = "YouTube Age-Range (Watch Time - Hours)"
        verbose_name_plural = "YouTube Age-Ranges (Watch Time - Hours)"
        unique_together = YouTubeAgeRangePercentage.Meta.unique_together
        ordering = YouTubeAgeRangePercentage.Meta.ordering


class YouTubeAgeRangeViewsPercentage(YouTubeAgeRangePercentage):
    """Demographics data of YouTube accounts, based on YouTube age range views
    percentage data.
    """

    class Meta:
        """Model meta options."""

        db_table = "youtube_age_range_views_percentage"
        verbose_name = "YouTube Age-Range (Views)"
        verbose_name_plural = "YouTube Age-Ranges (Views)"
        unique_together = YouTubeAgeRangePercentage.Meta.unique_together
        ordering = YouTubeAgeRangePercentage.Meta.ordering
