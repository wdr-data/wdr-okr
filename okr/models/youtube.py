"""Database models for YouTube."""

from django.db import models
from .base import Quintly


class YouTube(Quintly):
    """YouTube-Accounts, basierend auf Daten von Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "youtube"
        verbose_name = "YouTube-Account"
        verbose_name_plural = "YouTube-Accounts"
        ordering = Quintly.Meta.ordering

    bigquery_suffix = models.TextField(
        verbose_name="BigQuery Suffix",
        help_text="BigQuery Suffix, das im YouTube-Datentransfer in BigQuery konfiguriert wurde.",
    )


class YouTubeAnalytics(models.Model):
    """Performance-Daten gesamter YouTube-Accounts, basierend auf Daten von
    Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_analytics"
        verbose_name = "YouTube-Analytics"
        verbose_name_plural = "YouTube-Analytics"
        unique_together = ("youtube", "date")
        ordering = ["-date"]

    youtube = models.ForeignKey(
        verbose_name="YouTube-Account",
        help_text="Globale ID des YouTube-Accouts",
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="analytics",
        related_query_name="analytics",
    )
    date = models.DateField(verbose_name="Datum")

    views = models.IntegerField(verbose_name="Views", null=True)
    likes = models.IntegerField(verbose_name="Likes", null=True)
    dislikes = models.IntegerField(verbose_name="Dislikes", null=True)

    subscribers = models.IntegerField(verbose_name="Abonnent*innen (Gesamt)", null=True)
    subscribers_gained = models.IntegerField(
        verbose_name="Hinzugewonnene Abonnent*innen",
        null=True,
    )
    subscribers_lost = models.IntegerField(
        verbose_name="Verlorene Abonnent*innen",
        null=True,
    )

    watch_time = models.DurationField(
        verbose_name="Sehdauer Gesamt",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.youtube.name}"


class YouTubeDemographics(models.Model):
    """Demographiedaten gesamter YouTube-Accounts, basierend auf Daten von
    Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_demographics"
        verbose_name = "YouTube Demographics"
        verbose_name_plural = "YouTube Demographics"
        unique_together = ("youtube", "date", "age_range", "gender")
        ordering = ["-date", "gender", "age_range"]

    class AgeRange(models.TextChoices):
        # https://developers.google.com/youtube/analytics/dimensions#Demographic_Dimensions
        AGE_13_17 = "13-17", "13-17"
        AGE_18_24 = "18-24", "18-24"
        AGE_25_34 = "25-34", "25-34"
        AGE_35_44 = "35-44", "35-44"
        AGE_45_54 = "45-54", "45-54"
        AGE_55_64 = "55-64", "55-64"
        Age_65_ = "65+", "65+"

    class Gender(models.TextChoices):
        # https://developers.google.com/youtube/analytics/dimensions#Demographic_Dimensions
        MALE = "male", "Männlich"
        FEMALE = "female", "Weiblich"
        GENDER_OTHER = "other", "Andere Geschlechtsangabe"

    youtube = models.ForeignKey(
        verbose_name="YouTube-Account",
        help_text="Globale ID des YouTube-Accouts",
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="demographics",
        related_query_name="demographics",
    )
    date = models.DateField(verbose_name="Datum")

    age_range = models.CharField(
        verbose_name="Altersgruppe",
        choices=AgeRange.choices,
        help_text="Die Altersgruppe, für die dieser Datenpunkt gilt",
        max_length=20,
    )
    gender = models.CharField(
        verbose_name="Geschlecht",
        choices=Gender.choices,
        help_text="Das Geschlecht, für das dieser Datenpunkt gilt",
        max_length=20,
    )

    views_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        verbose_name="Anteil der Views",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.youtube.name} - {self.AgeRange(self.age_range).label}, {self.Gender(self.gender).label}"


class YouTubeTrafficSource(models.Model):
    """Traffic Source-Daten für einen YouTube-Account, basierend auf Daten von
    Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_traffic_source"
        verbose_name = "YouTube Traffic Source"
        verbose_name_plural = "YouTube Traffic Sources"
        unique_together = ("youtube", "date", "source_type")
        ordering = ["-date", "source_type"]

    class SourceType(models.TextChoices):
        # https://developers.google.com/youtube/analytics/dimensions#Traffic_Source_Dimensions
        ADVERTISING = "advertising", "Werbung"
        ANNOTATION = "annotation", "Annotation"
        CAMPAIGN_CARD = "campaign_card", "Kampagnenkarte"
        END_SCREEN = "end_screen", "Endscreen"
        EXT_URL = "ext_url", "Externe URL"
        NO_LINK_EMBEDDED = "no_link_embedded", "Kein Link (eingebettet)"
        NO_LINK_OTHER = "no_link_other", "Kein Link (sonstiges)"
        NOTIFICATION = "notification", "Benachrichtigung"
        PLAYLIST = "playlist", "Playlist"
        PROMOTED = "promoted", "Promoted"
        RELATED_VIDEO = "related_video", "Related"
        SHORTS = "shorts", "Shorts"
        SOUND_PAGE = "sound_page", "Soundpage"
        SUBSCRIBER = "subscriber", "Abonnent*in"
        YT_CHANNEL = "yt_channel", "Youtube-Kanal"
        YT_OTHER_PAGE = "yt_other_page", "Sonstige Youtube-Seite"
        YT_PLAYLIST_PAGE = "yt_playlist_page", "Youtube Playlist-Seite"
        YT_SEARCH = "yt_search", "Youtube-Suche"
        HASHTAGS = "hashtags", "Hashtags"

    youtube = models.ForeignKey(
        verbose_name="YouTube-Account",
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="traffic_sources",
        related_query_name="traffic_source",
    )

    date = models.DateField(verbose_name="Datum")

    source_type = models.CharField(
        verbose_name="Source Type",
        choices=SourceType.choices,
        max_length=40,
    )

    views = models.IntegerField(
        verbose_name="Views",
        null=True,
    )

    watch_time = models.DurationField(
        verbose_name="Sehdauer Gesamt",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.youtube.name} ({self.SourceType(self.source_type).label})"


class YouTubeVideo(models.Model):
    """Basisdaten einzelner YouTube-Videos, basierend auf Daten von
    Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_video"
        verbose_name = "YouTube-Video"
        verbose_name_plural = "YouTube-Videos"
        ordering = ["-published_at"]

    youtube = models.ForeignKey(
        verbose_name="YouTube-Account",
        help_text="Globale ID des YouTube-Accouts",
        to=YouTube,
        on_delete=models.CASCADE,
        related_name="videos",
        related_query_name="video",
    )

    external_id = models.CharField(
        verbose_name="Externe ID", max_length=32, unique=True
    )
    published_at = models.DateTimeField(
        verbose_name="Veröffentlichungszeitpunkt",
        null=True,
    )
    is_livestream = models.BooleanField(
        verbose_name="Livestream",
        help_text="Video als Livestream angelegt",
    )

    title = models.TextField(
        verbose_name="Titel",
        help_text="Titel des Videos",
    )
    description = models.TextField(
        verbose_name="Beschreibung",
        help_text="Beschreibungstext des Videos",
        blank=True,
    )
    duration = models.DurationField(
        verbose_name="Länge",
        help_text="Länge des Videos",
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.youtube.name} - {self.title}"


class YouTubeVideoAnalytics(models.Model):
    """Performance-Daten einzelner YouTube-Videos, basierend auf Daten von
    Youtube/BigQuery."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_video_analytics"
        verbose_name = "YouTube Video Analytics"
        verbose_name_plural = "YouTube Video Analytics"
        unique_together = ("youtube_video", "date", "live_or_on_demand")
        ordering = ["-date"]

    class LiveOrOnDemand(models.TextChoices):
        # https://developers.google.com/youtube/reporting/v1/reports/dimensions#Playback_Detail_Dimensions
        LIVE = "live", "Live"
        ON_DEMAND = "on_demand", "On demand"

    youtube_video = models.ForeignKey(
        verbose_name="YouTube-Video",
        help_text="ID des YouTube-Videos",
        to=YouTubeVideo,
        on_delete=models.CASCADE,
        related_name="analytics",
        related_query_name="analytics",
    )
    date = models.DateField(verbose_name="Datum")
    live_or_on_demand = models.CharField(
        verbose_name="Live oder on demand",
        choices=LiveOrOnDemand.choices,
        max_length=10,
    )

    views = models.IntegerField(verbose_name="Views")
    likes = models.IntegerField(verbose_name="Likes")
    dislikes = models.IntegerField(verbose_name="Dislikes")
    comments = models.IntegerField(verbose_name="Kommentare")
    shares = models.IntegerField(verbose_name="Shares")
    subscribers_gained = models.IntegerField(verbose_name="Verlorene Abonnent*innen")
    subscribers_lost = models.IntegerField(verbose_name="Gewonnene Abonnent*innen")
    watch_time = models.DurationField(verbose_name="Sehdauer Gesamt")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.youtube_video.youtube.name} - {self.youtube_video.title} (Analytics)"


class YouTubeVideoAnalyticsExtra(models.Model):
    """Performance-Daten einzelner YouTube-Videos, basierend auf manuell hochgeladenen
    Daten von Youtube."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_video_analytics_extra"
        verbose_name = "YouTube Video Analytics Extra"
        verbose_name_plural = "YouTube Video Analytics Extra"
        unique_together = ("youtube_video", "date")
        ordering = ["-date"]

    youtube_video = models.ForeignKey(
        verbose_name="YouTube-Video",
        help_text="ID des YouTube-Videos",
        to=YouTubeVideo,
        on_delete=models.CASCADE,
        related_name="analytics_extra",
        related_query_name="analytics_extra",
    )
    date = models.DateField(verbose_name="Datum")

    impressions = models.IntegerField(verbose_name="Impressions")
    clicks = models.IntegerField(verbose_name="Clicks")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.youtube_video.youtube.name} - {self.youtube_video.title} (Analytics Extra)"


class YouTubeVideoDemographics(models.Model):
    """Demographie-Daten einzelner YouTube-Videos, basierend auf Daten von
    Youtube/BigQuery (nur zu eingeloggten User*innen)."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_video_demographics"
        verbose_name = "YouTube Video Demographics"
        verbose_name_plural = "YouTube Video Demographics"
        unique_together = ("youtube_video", "age_range", "gender")
        ordering = ["youtube_video", "gender", "age_range"]

    class AgeRange(models.TextChoices):
        AGE_13_17 = "13-17", "13-17"
        AGE_18_24 = "18-24", "18-24"
        AGE_25_34 = "25-34", "25-34"
        AGE_35_44 = "35-44", "35-44"
        AGE_45_54 = "45-54", "45-54"
        AGE_55_64 = "55-64", "55-64"
        Age_65_ = "65+", "65+"

    class Gender(models.TextChoices):
        MALE = "male", "Männlich"
        FEMALE = "female", "Weiblich"
        GENDER_OTHER = "gender_other", "Andere Geschlechtsangabe"

    youtube_video = models.ForeignKey(
        verbose_name="YouTube-Video",
        help_text="ID des YouTube-Videos",
        to=YouTubeVideo,
        on_delete=models.CASCADE,
        related_name="demographics",
        related_query_name="demographics",
    )

    age_range = models.CharField(
        verbose_name="Altersgruppe",
        choices=AgeRange.choices,
        help_text="Die Altersgruppe, für die dieser Datenpunkt gilt",
        max_length=20,
    )
    gender = models.CharField(
        verbose_name="Geschlecht",
        choices=Gender.choices,
        help_text="Das Geschlecht, für das dieser Datenpunkt gilt",
        max_length=20,
    )

    views_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        verbose_name="Anteil der Views",
        null=True,
    )

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.youtube_video.youtube.name} - {self.youtube_video.title} {self.AgeRange(self.age_range).label}, {self.Gender(self.gender).label}"


class YouTubeVideoTrafficSource(models.Model):
    """Traffic Source-Daten einzelner YouTube-Videos, basierend auf Daten von
    Youtube/BigQuery."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_video_traffic_source"
        verbose_name = "YouTube Video Traffic Source"
        verbose_name_plural = "YouTube Video Traffic Source"
        unique_together = ("youtube_video", "source_type")
        ordering = ["source_type"]

    class SourceType(models.TextChoices):
        # https://developers.google.com/youtube/reporting/v1/reports/dimensions#Traffic_Source_Dimensions
        SOURCE_TYPE_0 = "0: Direct or unknown", "Direct or unknown"
        SOURCE_TYPE_1 = "1: YouTube advertising", "YouTube advertising"
        SOURCE_TYPE_3 = "3: Browse features", "Browse features"
        SOURCE_TYPE_4 = "4: YouTube channels", "YouTube channels"
        SOURCE_TYPE_5 = "5: YouTube search", "YouTube search"
        SOURCE_TYPE_7 = "7: Suggested videos", "Suggested videos"
        SOURCE_TYPE_8 = "8: Other YouTube features", "Other YouTube features"
        SOURCE_TYPE_9 = "9: External", "External"
        SOURCE_TYPE_11 = (
            "11: Video cards and annotations",
            "Video cards and annotations",
        )
        SOURCE_TYPE_14 = "14: Playlists", "Playlists"
        SOURCE_TYPE_17 = "17: Notifications", "Notifications"
        SOURCE_TYPE_18 = "18: Playlist pages", "Playlist pages"
        SOURCE_TYPE_19 = (
            "19: Programming from claimed content",
            "Programming from claimed content",
        )
        SOURCE_TYPE_20 = (
            "20: Interactive video endscreen",
            "Interactive video endscreen",
        )
        SOURCE_TYPE_23 = "23: Stories", "Stories"
        SOURCE_TYPE_24 = "24: Shorts", "Shorts"
        SOURCE_TYPE_25 = "25: Product Pages", "Product Pages"
        SOURCE_TYPE_26 = "26: Hashtag Pages", "Hashtag Pages"
        SOURCE_TYPE_27 = "27: Sound Pages", "Sound Pages"

    youtube_video = models.ForeignKey(
        verbose_name="YouTube-Video",
        help_text="ID des YouTube-Videos",
        to=YouTubeVideo,
        on_delete=models.CASCADE,
        related_name="traffic_sources",
        related_query_name="traffic_source",
    )

    source_type = models.CharField(
        verbose_name="Source Type",
        choices=SourceType.choices,
        max_length=40,
    )

    views = models.IntegerField(verbose_name="Views")

    watch_time = models.DurationField(verbose_name="Sehdauer Gesamt")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.youtube_video.youtube.name} - {self.youtube_video.title} ({self.SourceType(self.source_type).label})"


class YouTubeVideoSearchTerm(models.Model):
    """Top Suchanfragen für einzelne YouTube-Videos, basierend auf Daten von
    Youtube/BigQuery."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_video_search_term"
        verbose_name = "YouTube Video Search Term"
        verbose_name_plural = "YouTube Video Search Terms"
        unique_together = ("youtube_video", "search_term")
        ordering = ["youtube_video", "search_term"]

    youtube_video = models.ForeignKey(
        verbose_name="YouTube-Video",
        help_text="ID des YouTube-Videos",
        to=YouTubeVideo,
        on_delete=models.CASCADE,
        related_name="search_terms",
        related_query_name="search_term",
    )

    search_term = models.TextField(verbose_name="Suche")

    views = models.IntegerField(verbose_name="Views")

    watch_time = models.DurationField(verbose_name="Sehdauer Gesamt")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.youtube_video.youtube.name} - {self.youtube_video.title}: {self.search_term}"


class YouTubeVideoExternalTraffic(models.Model):
    """Externe Traffic Sources für einzelne YouTube-Videos, basierend auf Daten von
    Youtube/BigQuery."""

    class Meta:
        """Model meta options."""

        db_table = "youtube_video_external_traffic"
        verbose_name = "YouTube Video External Traffic"
        verbose_name_plural = "YouTube Video External Traffic"
        unique_together = ("youtube_video", "name")
        ordering = ["name"]

    youtube_video = models.ForeignKey(
        verbose_name="YouTube-Video",
        help_text="ID des YouTube-Videos",
        to=YouTubeVideo,
        on_delete=models.CASCADE,
        related_name="external_traffic",
        related_query_name="external_traffic",
    )

    name = models.TextField(verbose_name="Traffic Source")

    views = models.IntegerField(verbose_name="Views")

    watch_time = models.DurationField(verbose_name="Sehdauer Gesamt")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.youtube_video.youtube.name} - {self.youtube_video.title}: {self.search_term}"
