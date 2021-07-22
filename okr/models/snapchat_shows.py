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
        helptext="The number of unique users who saw this show on this date.",
    )
    monthly_uniques = models.IntegerField(
        helptext="The number of unique users who saw this show in the context of the month before this date.",
    )
    subscribers = models.IntegerField(
        helptext="The number of the show's subscribers on this date",
    )
    loyal_users = models.IntegerField(
        helptext="The number of users that browsed the shows's content 5 to 7 days in the context of the previous 7 days from this date.",
    )
    frequent_users = models.IntegerField(
        helptext="The number of users that browsed the shows's content 3 to 4 days in the context of the previous 7 days from this date.",
    )
    returning_users = models.IntegerField(
        helptext="The number of users that browsed the shows's content twice in the context of the previous 7 days from this date.",
    )
    new_users = models.IntegerField(
        helptext="The number of users that browsed the shows's content once in the context of the previous 7 days from this date.",
    )

    gender_demographics_male = models.IntegerField(
        helptext="The number of male users who saw this show on this date.",
    )
    gender_demographics_female = models.IntegerField(
        helptext="The number of female users who saw this show on this date.",
    )
    gender_demographics_unknown = models.IntegerField(
        helptext="The number of users with unknown gender who saw this show on this date.",
    )

    age_demographics_13_to_17 = models.IntegerField(
        helptext="The number of users in the age group 13 to 17 years who saw this show on this date.",
    )
    age_demographics_18_to_24 = models.IntegerField(
        helptext="The number of users in the age group 18 to 24 years who saw this show on this date.",
    )
    age_demographics_25_to_34 = models.IntegerField(
        helptext="The number of users in the age group 25 to 34 years who saw this show on this date.",
    )
    age_demographics_35_plus = models.IntegerField(
        helptext="The number of users in the age group 35 and older years who saw this show on this date.",
    )
    age_demographics_unknown = models.IntegerField(
        helptext="The number of users with unknown age who saw this show on this date.",
    )

    total_time_viewed = models.DurationField(
        helptext="The total time users spent on this show's content.",
    )
    average_time_spent_per_user = models.DurationField(
        helptext="The average time users spent on this show's content per user.",
    )
    unique_topsnaps_per_user = models.IntegerField(
        helptext="The average number of topsnaps viewed in this show's stories.",
    )
    unique_topsnap_views = models.IntegerField(
        helptext="The total number of unique topsnap views by users that engaged with this show's content.",
    )
    topsnap_views = models.IntegerField(
        helptext="The total number of topsnap views by users that engaged with this show's content.",
    )
    attachment_conversion = models.DecimalField(
        helptext="The percentage of unique users that swiped up on this show's snaps with attachments.",
    )
    attachment_article_views = models.IntegerField(
        helptext="The total number of attachment article views by users that engaged with this show's content.",
    )
    attachment_video_views = models.IntegerField(
        helptext="The total number of attachment video views by users that engaged with this show's content.",
    )
    screenshots = models.IntegerField(
        helptext="The total number of screenshots made of this show's content on this date.",
    )
    shares = models.IntegerField(
        helptext="The total number of shares of this show's content on this date.",
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.snapchatshow.name}"


class SnapchatShowStory(models.Model):
    """Grundlegende Daten zu einzelnen Snapchat Show Stories."""

    class Meta:
        """Model meta options."""

        db_table = "snapchat_show_story"
        verbose_name = "Snapchat Show Story"
        verbose_name_plural = "Snapchat Show Stories"
        ordering = ["-created_at"]

    class State(models.TextChoices):
        """Possible states of a story."""

        AVAILABLE = "available", "Verfügbar"
        SCHEDULED = "scheduled", "Geplant"

    external_id = models.CharField(
        helptext="The ID of this snap.",
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
        helptext="The time this story was created.",
    )
    start_date_time = models.DateTimeField(
        helptext="The time this story was published.",
    )
    first_live_date_time = models.DateTimeField(
        helptext="The time this story went live for the first time. This is usually only seconds after it was published.",
    )

    spotlight_end_date_time = models.DateTimeField(
        helptext="The time this story stopped being the show's most recent story.",
    )
    spotlight_duration = models.DurationField(
        helptext="The total time this story was the shows's most recent story.",
    )

    title = models.TextField(
        helptext="The title of this story.",
    )
    state = models.CharField(
        helptext="The state of this story. One of: Available, Scheduled",
    )

    gender_demographics_male = models.IntegerField(
        helptext="The number of male users who saw this story.",
    )
    gender_demographics_female = models.IntegerField(
        helptext="The number of female users who saw this story.",
    )
    gender_demographics_unknown = models.IntegerField(
        helptext="The number of users with unknown gender who saw this story.",
    )

    age_demographics_13_to_17 = models.IntegerField(
        helptext="The number of users in the age group 13 to 17 years who saw this story.",
    )
    age_demographics_18_to_24 = models.IntegerField(
        helptext="The number of users in the age group 18 to 24 years who saw this story.",
    )
    age_demographics_25_to_34 = models.IntegerField(
        helptext="The number of users in the age group 25 to 34 years who saw this story.",
    )
    age_demographics_35_plus = models.IntegerField(
        helptext="The number of users in the age group 35 and older years who saw this story.",
    )
    age_demographics_unknown = models.IntegerField(
        helptext="The number of users with unknown age who saw this story.",
    )

    view_time = models.DurationField(
        helptext="The total time this story was viewed.",
    )
    average_view_time_per_user = models.DurationField(
        helptext="The average time per user this story was viewed.",
    )
    total_views = models.IntegerField(
        helptext="The total number of views for this story.",
    )
    unique_viewers = models.IntegerField(
        helptext="The total number of unique viewers for this story.",
    )
    unique_completers = models.IntegerField(
        helptext="The total number of users who completely watched this story.",
    )
    completion_rate = models.DecimalField(
        helptext="The percentage of users who completely watched this story.",
    )
    shares = models.IntegerField(
        helptext="The total number of shares for this story.",
    )
    unique_sharers = models.IntegerField(
        helptext="The total number of users sharing this story.",
    )
    viewers_from_shares = models.IntegerField(
        helptext="The total number of users viewing this story from a share.",
    )
    screenshots = models.IntegerField(
        helptext="The total number of screenshots made of this story.",
    )
    subscribers = models.IntegerField(
        helptext="The total number of new subscribers to your show added when this story was live.",
    )
    topsnap_view_time = models.DurationField(
        helptext="The total time topsnaps of this story were viewed.",
    )
    topsnap_average_view_time_per_user = models.DurationField(
        helptext="The average time per user topsnaps of this story were viewed.",
    )
    topsnap_total_views = models.IntegerField(
        helptext="The total number of views for topsnaps of this story.",
    )
    topsnap_unique_views = models.IntegerField(
        helptext="The total number of unique views for topsnaps of this story.",
    )
    unique_topsnaps_per_user = models.IntegerField(
        helptext="The average number of topsnaps viewed per user in this story.",
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
        helptext="The ID of this snap.",
        max_length=32,
        unique=True,
    )
    story = models.ForeignKey(
        verbose_name="Snapchat Show Story",
        helptext="The ID of the story this snap belongs to.",
    )

    name = models.TextField(
        helptext="The name of this snap.",
        null=True,
    )
    position = models.IntegerField(
        helptext="The position of this snap within the story. The first snap has position 1.",
    )
    duration = models.DurationField(
        helptext="The duration of this snap.",
    )
    subscribe_options_headline = models.TextField(
        helptext="The headline of the call to action to subscribe to the show present on this snap.",
    )
    tiles = models.IntegerField(
        helptext="The number of tiles related to this snap.",
    )

    gender_demographics_male = models.IntegerField(
        helptext="The number of male users who saw this snap.",
    )
    gender_demographics_female = models.IntegerField(
        helptext="The number of female users who saw this snap.",
    )
    gender_demographics_unknown = models.IntegerField(
        helptext="The number of users with unknown gender who saw this snap.",
    )

    age_demographics_13_to_17 = models.IntegerField(
        helptext="The number of users in the age group 13 to 17 years who saw this snap.",
    )
    age_demographics_18_to_24 = models.IntegerField(
        helptext="The number of users in the age group 18 to 24 years who saw this snap.",
    )
    age_demographics_25_to_34 = models.IntegerField(
        helptext="The number of users in the age group 25 to 34 years who saw this snap.",
    )
    age_demographics_35_plus = models.IntegerField(
        helptext="The number of users in the age group 35 and older years who saw this snap.",
    )
    age_demographics_unknown = models.IntegerField(
        helptext="The number of users with unknown age who saw this snap.",
    )

    view_time = models.DurationField(
        helptext="The total time this snap was viewed.",
    )
    average_view_time_per_user = models.DurationField(
        helptext="The average time per user this snap was viewed.",
    )
    total_views = models.IntegerField(
        helptext="The total number of views for this snap.",
    )
    unique_viewers = models.IntegerField(
        helptext="The total number of unique viewers for this snap.",
    )
    unique_completers = models.IntegerField(
        helptext="The total number of users who completely watched this snap.",
    )
    completion_rate = models.DecimalField(
        helptext="The percentage of users who completely watched this snap.",
    )
    shares = models.IntegerField(
        helptext="The total number of shares for this snap.",
    )
    unique_sharers = models.IntegerField(
        helptext="The total number of users sharing this snap.",
    )
    viewers_from_shares = models.IntegerField(
        helptext="The total number of users viewing this story from a snap.",
    )
    screenshots = models.IntegerField(
        helptext="The total number of screenshots made of this snap.",
    )
    drop_off_rate = models.DecimalField(
        helptext="The percentage of users that dropped off from this snap to the next.",
    )
    topsnap_view_time = models.DurationField(
        helptext="The total time topsnaps related to this snap were viewed.",
    )
    topsnap_average_view_time_per_user = models.DurationField(
        helptext="The average time per user topsnaps related to this snap were viewed.",
    )
    topsnap_total_views = models.IntegerField(
        helptext="The total number of views for topsnaps related to this snap.",
    )
    topsnap_unique_views = models.IntegerField(
        helptext="The total number of unique views for topsnaps related to this snap.",
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
