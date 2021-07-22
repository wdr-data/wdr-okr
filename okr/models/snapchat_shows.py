"""Database models for Snapchat Shows."""

from django.db import models
from .base import Quintly


class SnapchatShow(Quintly):
    """Snapchat Show Accounts, basierend auf Daten von Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "snapchatshow"
        verbose_name = "Snapchat Show Account"
        verbose_name_plural = "Snapchat Show Accounts"
        ordering = Quintly.Meta.ordering


class SnapchatShowInsight(models.Model):
    """Performance-Daten einzelner Snapchat Show Accounts, basierend auf Daten von Quintly
    Insights.
    """

    class Meta:
        """Model meta options."""

        db_table = "snapchat_show_insights"
        verbose_name = "Snapchat Show Insight"
        verbose_name_plural = "Snapchat Show Insights"
        unique_together = ("snapchat_show", "date")
        ordering = ["-date"]

    snapchat_show = models.ForeignKey(
        verbose_name="Snapchat Show Account",
        help_text="Globale ID des Snapchat Show Accounts",
        to=SnapchatShow,
        on_delete=models.CASCADE,
        related_name="insights",
        related_query_name="insight",
    )
    date = models.DateField(verbose_name="Datum")

    daily_uniques = models.IntegerField(
        help_text="The number of unique users who saw this show on this date.",
        null=True,
    )
    monthly_uniques = models.IntegerField(
        help_text="The number of unique users who saw this show in the context of the month before this date.",
        null=True,
    )
    subscribers = models.IntegerField(
        help_text="The number of the show's subscribers on this date",
        null=True,
    )
    loyal_users = models.IntegerField(
        help_text="The number of users that browsed the shows's content 5 to 7 days in the context of the previous 7 days from this date.",
        null=True,
    )
    frequent_users = models.IntegerField(
        help_text="The number of users that browsed the shows's content 3 to 4 days in the context of the previous 7 days from this date.",
        null=True,
    )
    returning_users = models.IntegerField(
        help_text="The number of users that browsed the shows's content twice in the context of the previous 7 days from this date.",
        null=True,
    )
    new_users = models.IntegerField(
        help_text="The number of users that browsed the shows's content once in the context of the previous 7 days from this date.",
        null=True,
    )

    gender_demographics_male = models.IntegerField(
        help_text="The number of male users who saw this show on this date.",
        null=True,
    )
    gender_demographics_female = models.IntegerField(
        help_text="The number of female users who saw this show on this date.",
        null=True,
    )
    gender_demographics_unknown = models.IntegerField(
        help_text="The number of users with unknown gender who saw this show on this date.",
        null=True,
    )

    age_demographics_13_to_17 = models.IntegerField(
        help_text="The number of users in the age group 13 to 17 years who saw this show on this date.",
        null=True,
    )
    age_demographics_18_to_24 = models.IntegerField(
        help_text="The number of users in the age group 18 to 24 years who saw this show on this date.",
        null=True,
    )
    age_demographics_25_to_34 = models.IntegerField(
        help_text="The number of users in the age group 25 to 34 years who saw this show on this date.",
        null=True,
    )
    age_demographics_35_plus = models.IntegerField(
        help_text="The number of users in the age group 35 and older years who saw this show on this date.",
        null=True,
    )
    age_demographics_unknown = models.IntegerField(
        help_text="The number of users with unknown age who saw this show on this date.",
        null=True,
    )

    total_time_viewed = models.DurationField(
        help_text="The total time users spent on this show's content.",
        null=True,
    )
    average_time_spent_per_user = models.DurationField(
        help_text="The average time users spent on this show's content per user.",
        null=True,
    )
    unique_topsnaps_per_user = models.IntegerField(
        help_text="The average number of topsnaps viewed in this show's stories.",
        null=True,
    )
    unique_topsnap_views = models.IntegerField(
        help_text="The total number of unique topsnap views by users that engaged with this show's content.",
        null=True,
    )
    topsnap_views = models.IntegerField(
        help_text="The total number of topsnap views by users that engaged with this show's content.",
        null=True,
    )
    attachment_conversion = models.DecimalField(
        help_text="The percentage of unique users that swiped up on this show's snaps with attachments.",
        null=True,
        decimal_places=5,
        max_digits=6,
    )
    attachment_article_views = models.IntegerField(
        help_text="The total number of attachment article views by users that engaged with this show's content.",
        null=True,
    )
    attachment_video_views = models.IntegerField(
        help_text="The total number of attachment video views by users that engaged with this show's content.",
        null=True,
    )
    screenshots = models.IntegerField(
        help_text="The total number of screenshots made of this show's content on this date.",
        null=True,
    )
    shares = models.IntegerField(
        help_text="The total number of shares of this show's content on this date.",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.snapchat_show.name}"


class SnapchatShowStory(models.Model):
    """Grundlegende Daten zu einzelnen Snapchat Show Stories."""

    class Meta:
        """Model meta options."""

        db_table = "snapchat_show_story"
        verbose_name = "Snapchat Show Story"
        verbose_name_plural = "Snapchat Show Stories"
        ordering = ["-start_date_time"]

    class State(models.TextChoices):
        """Possible states of a story."""

        AVAILABLE = "available", "Verfügbar"
        SCHEDULED = "scheduled", "Geplant"

    external_id = models.CharField(
        help_text="The ID of this snap.",
        max_length=32,
        unique=True,
    )
    snapchat_show = models.ForeignKey(
        verbose_name="Snapchat Show Account",
        help_text="Globale ID des Snapchat Show Accounts",
        to=SnapchatShow,
        on_delete=models.CASCADE,
        related_name="stories",
        related_query_name="story",
    )

    create_date_time = models.DateTimeField(
        help_text="The time this story was created.",
        null=True,
    )
    start_date_time = models.DateTimeField(
        help_text="The time this story was published.",
        null=True,
    )
    first_live_date_time = models.DateTimeField(
        help_text="The time this story went live for the first time. This is usually only seconds after it was published.",
        null=True,
    )

    spotlight_end_date_time = models.DateTimeField(
        help_text="The time this story stopped being the show's most recent story.",
        null=True,
    )
    spotlight_duration = models.DurationField(
        help_text="The total time this story was the shows's most recent story.",
        null=True,
    )

    title = models.TextField(
        help_text="The title of this story.",
    )
    state = models.CharField(
        help_text="The state of this story. One of: Available, Scheduled",
        choices=State.choices,
        max_length=9,
    )

    gender_demographics_male = models.IntegerField(
        help_text="The number of male users who saw this story.",
        null=True,
    )
    gender_demographics_female = models.IntegerField(
        help_text="The number of female users who saw this story.",
        null=True,
    )
    gender_demographics_unknown = models.IntegerField(
        help_text="The number of users with unknown gender who saw this story.",
        null=True,
    )

    age_demographics_13_to_17 = models.IntegerField(
        help_text="The number of users in the age group 13 to 17 years who saw this story.",
        null=True,
    )
    age_demographics_18_to_24 = models.IntegerField(
        help_text="The number of users in the age group 18 to 24 years who saw this story.",
        null=True,
    )
    age_demographics_25_to_34 = models.IntegerField(
        help_text="The number of users in the age group 25 to 34 years who saw this story.",
        null=True,
    )
    age_demographics_35_plus = models.IntegerField(
        help_text="The number of users in the age group 35 and older years who saw this story.",
        null=True,
    )
    age_demographics_unknown = models.IntegerField(
        help_text="The number of users with unknown age who saw this story.",
        null=True,
    )

    view_time = models.DurationField(
        help_text="The total time this story was viewed.",
        null=True,
    )
    average_view_time_per_user = models.DurationField(
        help_text="The average time per user this story was viewed.",
        null=True,
    )
    total_views = models.IntegerField(
        help_text="The total number of views for this story.",
        null=True,
    )
    unique_viewers = models.IntegerField(
        help_text="The total number of unique viewers for this story.",
        null=True,
    )
    unique_completers = models.IntegerField(
        help_text="The total number of users who completely watched this story.",
        null=True,
    )
    completion_rate = models.DecimalField(
        help_text="The percentage of users who completely watched this story.",
        null=True,
        decimal_places=5,
        max_digits=6,
    )
    shares = models.IntegerField(
        help_text="The total number of shares for this story.",
        null=True,
    )
    unique_sharers = models.IntegerField(
        help_text="The total number of users sharing this story.",
        null=True,
    )
    viewers_from_shares = models.IntegerField(
        help_text="The total number of users viewing this story from a share.",
        null=True,
    )
    screenshots = models.IntegerField(
        help_text="The total number of screenshots made of this story.",
        null=True,
    )
    subscribers = models.IntegerField(
        help_text="The total number of new subscribers to your show added when this story was live.",
        null=True,
    )
    topsnap_view_time = models.DurationField(
        help_text="The total time topsnaps of this story were viewed.",
        null=True,
    )
    topsnap_average_view_time_per_user = models.DurationField(
        help_text="The average time per user topsnaps of this story were viewed.",
        null=True,
    )
    topsnap_total_views = models.IntegerField(
        help_text="The total number of views for topsnaps of this story.",
        null=True,
    )
    topsnap_unique_views = models.IntegerField(
        help_text="The total number of unique views for topsnaps of this story.",
        null=True,
    )
    unique_topsnaps_per_user = models.IntegerField(
        help_text="The average number of topsnaps viewed per user in this story.",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.start_date_time}: {self.snapchat_show.name} - {self.title}"


'''
class SnapchatShowSnap(models.Model):
    """Grundlegende Daten zu einzelnen Snaps."""

    class Meta:
        """Model meta options."""

        db_table = "snapchat_show_snap"
        verbose_name = "Snapchat Show Snap"
        verbose_name_plural = "Snapchat Show Snaps"
        ordering = ["-created_at"]

    external_id = models.CharField(
        help_text="The ID of this snap.",
        max_length=32,
        unique=True,
    )
    story = models.ForeignKey(
        verbose_name="Snapchat Show Story",
        help_text="The ID of the story this snap belongs to.",
    )

    name = models.TextField(
        help_text="The name of this snap.",
        null=True,
    )
    position = models.IntegerField(
        help_text="The position of this snap within the story. The first snap has position 1.",
        null=True,
    )
    duration = models.DurationField(
        help_text="The duration of this snap.",
        null=True,
    )
    subscribe_options_headline = models.TextField(
        help_text="The headline of the call to action to subscribe to the show present on this snap.",
        null=True,
    )
    tiles = models.IntegerField(
        help_text="The number of tiles related to this snap.",
        null=True,
    )

    gender_demographics_male = models.IntegerField(
        help_text="The number of male users who saw this snap.",
        null=True,
    )
    gender_demographics_female = models.IntegerField(
        help_text="The number of female users who saw this snap.",
        null=True,
    )
    gender_demographics_unknown = models.IntegerField(
        help_text="The number of users with unknown gender who saw this snap.",
        null=True,
    )

    age_demographics_13_to_17 = models.IntegerField(
        help_text="The number of users in the age group 13 to 17 years who saw this snap.",
        null=True,
    )
    age_demographics_18_to_24 = models.IntegerField(
        help_text="The number of users in the age group 18 to 24 years who saw this snap.",
        null=True,
    )
    age_demographics_25_to_34 = models.IntegerField(
        help_text="The number of users in the age group 25 to 34 years who saw this snap.",
        null=True,
    )
    age_demographics_35_plus = models.IntegerField(
        help_text="The number of users in the age group 35 and older years who saw this snap.",
        null=True,
    )
    age_demographics_unknown = models.IntegerField(
        help_text="The number of users with unknown age who saw this snap.",
        null=True,
    )

    view_time = models.DurationField(
        help_text="The total time this snap was viewed.",
        null=True,
    )
    average_view_time_per_user = models.DurationField(
        help_text="The average time per user this snap was viewed.",
        null=True,
    )
    total_views = models.IntegerField(
        help_text="The total number of views for this snap.",
        null=True,
    )
    unique_viewers = models.IntegerField(
        help_text="The total number of unique viewers for this snap.",
        null=True,
    )
    unique_completers = models.IntegerField(
        help_text="The total number of users who completely watched this snap.",
        null=True,
    )
    completion_rate = models.DecimalField(
        help_text="The percentage of users who completely watched this snap.",
        null=True,
        decimal_places=5,
        max_digits=6,
    )
    shares = models.IntegerField(
        help_text="The total number of shares for this snap.",
        null=True,
    )
    unique_sharers = models.IntegerField(
        help_text="The total number of users sharing this snap.",
        null=True,
    )
    viewers_from_shares = models.IntegerField(
        help_text="The total number of users viewing this story from a snap.",
        null=True,
    )
    screenshots = models.IntegerField(
        help_text="The total number of screenshots made of this snap.",
        null=True,
    )
    drop_off_rate = models.DecimalField(
        help_text="The percentage of users that dropped off from this snap to the next.",
        null=True,
        decimal_places=5,
        max_digits=6,
    )
    topsnap_view_time = models.DurationField(
        help_text="The total time topsnaps related to this snap were viewed.",
        null=True,
    )
    topsnap_average_view_time_per_user = models.DurationField(
        help_text="The average time per user topsnaps related to this snap were viewed.",
        null=True,
    )
    topsnap_total_views = models.IntegerField(
        help_text="The total number of views for topsnaps related to this snap.",
        null=True,
    )
    topsnap_unique_views = models.IntegerField(
        help_text="The total number of unique views for topsnaps related to this snap.",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.story.start_date_time}: {self.story.title} - {self.position}"
'''
