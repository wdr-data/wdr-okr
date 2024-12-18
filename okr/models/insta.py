"""Database models for Instagram."""

from django.db import models
from .base import Quintly


class Insta(Quintly):
    """Instagram-Accounts, basierend auf Daten von Quintly."""

    class Meta:
        """Model meta options."""

        db_table = "instagram"
        verbose_name = "Instagram-Account"
        verbose_name_plural = "Instagram-Accounts"
        ordering = Quintly.Meta.ordering


class InstaInsight(models.Model):
    """Performance-Daten einzelner Instagram-Accounts, basierend auf Daten von Instagram
    Insights.
    """

    class Meta:
        """Model meta options."""

        db_table = "instagram_insights"
        verbose_name = "Instagram-Insight"
        verbose_name_plural = "Instagram-Insights"
        unique_together = ("insta", "date")
        ordering = ["-date"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="insights",
        related_query_name="insight",
    )
    date = models.DateField(verbose_name="Datum")

    reach = models.IntegerField(verbose_name="Reichweite", null=True)
    reach_7_days = models.IntegerField(
        verbose_name="Reichweite (7 Tage rollierend)",
        null=True,
    )
    reach_28_days = models.IntegerField(
        verbose_name="Reichweite (28 Tage rollierend)",
        null=True,
    )

    impressions = models.IntegerField(verbose_name="Impressions", null=True)
    followers = models.IntegerField(verbose_name="Follower", null=True)
    text_message_clicks_day = models.IntegerField(
        verbose_name="Nachricht senden", null=True
    )
    email_contacts_day = models.IntegerField(verbose_name="Email senden", null=True)
    profile_views = models.IntegerField(verbose_name="Profilansichten", null=True)

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.insta.name}"


class InstaPost(models.Model):
    """Grundlegende Daten zu einzelnen Instagram-Postings."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_post"
        verbose_name = "Instagram-Post"
        verbose_name_plural = "Instagram-Posts"
        ordering = ["-created_at"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="post",
    )
    external_id = models.CharField(
        verbose_name="Externe ID", max_length=25, unique=True
    )
    message = models.TextField(verbose_name="Text", help_text="Volltext des Postings")
    created_at = models.DateTimeField(verbose_name="Erstellungsdatum")
    post_type = models.CharField(
        verbose_name="Typ",
        help_text="Art des Postings (Image, Carousel, etc)",
        max_length=20,
    )
    comments = models.IntegerField(
        verbose_name="Kommentare",
        help_text="Anzahl der Kommentare",
        null=True,
    )
    likes = models.IntegerField(
        verbose_name="Likes",
        help_text="Anzahl der Likes",
        null=True,
    )
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        null=True,
    )
    saved = models.IntegerField(
        verbose_name="Saves",
        help_text="Anzahl der Saves",
        null=True,
    )
    video_views = models.IntegerField(
        verbose_name="Video-Views",
        help_text="Video-Views (3 sec oder mehr)",
        null=True,
    )
    shares = models.IntegerField(
        verbose_name="Shares",
        help_text="Organische Shares, nur für Reels verfügbar",
        null=True,
    )
    link = models.URLField(verbose_name="Link", help_text="URL des Postings")
    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.insta.name} - {self.post_type}"


class InstaVideoData(models.Model):
    """Tägliche Daten zu einzelnen Instagram Posts vom Typ "Video"."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_video_data"
        verbose_name = "Instagram Video-Daten"
        verbose_name_plural = "Instagram Video-Daten"
        ordering = ["-date"]
        unique_together = ("post", "date")

    post = models.ForeignKey(
        verbose_name="Post",
        help_text="Globale ID des Posts",
        to=InstaPost,
        on_delete=models.CASCADE,
        related_name="video_data",
        related_query_name="video_data",
    )
    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum des Datenpunkts",
    )

    comments = models.IntegerField(
        verbose_name="Kommentare",
        help_text="Anzahl der Kommentare",
        null=True,
    )
    likes = models.IntegerField(
        verbose_name="Likes",
        help_text="Anzahl der Likes",
        null=True,
    )
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        null=True,
    )
    saved = models.IntegerField(
        verbose_name="Saves",
        help_text="Anzahl der Saves",
        null=True,
    )
    video_views = models.IntegerField(
        verbose_name="Video-Views",
        help_text="Video-Views (3 sec oder mehr)",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )

    def __str__(self):
        return f"{self.date}: {self.post.message[:15]}..."


class InstaReelData(models.Model):
    """Tägliche Daten zu einzelnen Instagram Posts vom Typ "Reel"."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_reel_data"
        verbose_name = "Instagram Reel-Daten"
        verbose_name_plural = "Instagram Reel-Daten"
        ordering = ["-date"]
        unique_together = ("post", "date")

    post = models.ForeignKey(
        verbose_name="Post",
        help_text="Globale ID des Posts",
        to=InstaPost,
        on_delete=models.CASCADE,
        related_name="reel_data",
        related_query_name="reel_data",
    )
    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum des Datenpunkts",
    )

    comments = models.IntegerField(
        verbose_name="Kommentare",
        help_text="Anzahl der Kommentare",
        null=True,
    )
    likes = models.IntegerField(
        verbose_name="Likes",
        help_text="Anzahl der Likes",
        null=True,
    )
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    saved = models.IntegerField(
        verbose_name="Saves",
        help_text="Anzahl der Saves",
        null=True,
    )
    video_views = models.IntegerField(
        verbose_name="Video-Views",
        help_text="Video-Views (3 sec oder mehr)",
        null=True,
    )
    shares = models.IntegerField(
        verbose_name="Shares",
        help_text="Organische Shares",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )

    def __str__(self):
        return f"{self.date}: {self.post.message[:15]}..."


class InstaStory(models.Model):
    """Daten zu einzelnen Instagram Stories.

    Jede Zeile der Datenbank enthält Daten zu einem Story-Element. Eine Insta-Story
    besteht in der Regel aus mehreren Story-Elementen.
    """

    class Meta:
        """Model meta options."""

        db_table = "instagram_story"
        verbose_name = "Instagram-Story"
        verbose_name_plural = "Instagram-Stories"
        ordering = ["-created_at"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="stories",
        related_query_name="story",
    )
    external_id = models.CharField(
        verbose_name="Externe ID",
        max_length=25,
        unique=True,
    )
    caption = models.TextField(
        verbose_name="Text",
        help_text="Volltext des Story-Elements",
        null=True,
    )
    created_at = models.DateTimeField(verbose_name="Erstellungszeitpunkt")
    story_type = models.CharField(
        verbose_name="Typ",
        help_text="Art des Story-Elements (Image/Video)",
        max_length=200,
    )
    replies = models.IntegerField(
        verbose_name="Antworten",
        help_text="Anzahl der Antworten",
        null=True,
    )
    exits = models.IntegerField(
        verbose_name="Exits",
        help_text="Anzahl der Ausstiege",
        null=True,
    )
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        null=True,
    )
    taps_forward = models.IntegerField(
        verbose_name="Taps forward",
        help_text="Anzahl der forward Taps",
        null=True,
    )
    taps_back = models.IntegerField(
        verbose_name="Taps back",
        help_text="Anzahl der back Taps",
        null=True,
    )
    link = models.URLField(
        verbose_name="Link",
        help_text="URL des Story-Elements",
        max_length=1024,
    )
    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.insta.name} - {self.story_type}"


class InstaIGTV(models.Model):
    """Grundlegende Daten zu einzelnen Instagram IGTV Videos."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_tv_video"
        verbose_name = "Instagram IGTV Video"
        verbose_name_plural = "Instagram IGTV Videos"
        ordering = ["-created_at"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="igtv_videos",
        related_query_name="igtv_video",
    )
    external_id = models.CharField(
        verbose_name="Externe ID",
        max_length=25,
        unique=True,
    )
    created_at = models.DateTimeField(verbose_name="Erstellungsdatum")
    message = models.TextField(
        verbose_name="Text",
        help_text="Beschreibungstext des IGTV Videos",
    )
    video_title = models.TextField(
        verbose_name="Titel",
        help_text="Titel des IGTV Videos",
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
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        null=True,
    )
    saved = models.IntegerField(
        verbose_name="Saves",
        help_text="Anzahl der Saves",
        null=True,
    )
    video_views = models.IntegerField(
        verbose_name="Likes",
        help_text="Video-Views (3 sec oder mehr)",
        null=True,
    )
    link = models.URLField(verbose_name="Link", help_text="URL des Postings")
    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.created_at}: {self.insta.name} - {self.video_title}"


class InstaIGTVData(models.Model):
    """Tägliche Daten zu einzelnen Instagram IGTV Videos."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_tv_video_data"
        verbose_name = "Instagram IGTV Video-Daten"
        verbose_name_plural = "Instagram IGTV Video-Daten"
        ordering = ["-date"]
        unique_together = ("igtv", "date")

    igtv = models.ForeignKey(
        verbose_name="IGTV",
        help_text="Globale ID des IGTV",
        to=InstaIGTV,
        on_delete=models.CASCADE,
        related_name="data",
        related_query_name="data",
    )
    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum des Datenpunkts",
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
    reach = models.IntegerField(
        verbose_name="Reichweite",
        null=True,
    )
    impressions = models.IntegerField(
        verbose_name="Impressions",
        null=True,
    )
    saved = models.IntegerField(
        verbose_name="Saves",
        help_text="Anzahl der Saves",
        null=True,
    )
    video_views = models.IntegerField(
        verbose_name="Likes",
        help_text="Video-Views (3 sec oder mehr)",
        null=True,
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )

    def __str__(self):
        return f"{self.date}: {self.igtv.video_title}"


class InstaComment(models.Model):
    """
    Enthält Daten zu einzelnen Kommentaren.

    Diese Daten werden von Quintly aus der Tabelle "instagramInsightsComments"
    (siehe https://api.quintly.com/#instagramInsightsComments) bezogen.
    Allerdings nehmen wir nur die Kommentare auf, die wir einem Post zuordnen
    können, und daher grundsätzlich nicht die Kommentare auf IGTV-Videos.

    Grund dafür ist, dass IGTV eingestellt wird und daher in Zukunft keine
    Bedeutung mehr haben wird. Falls für die Vergangenheit Unterschiede zu
    Auswertungen in Quintly auftreten, ist dies die Ursache.
    """

    class Meta:
        """Model meta options."""

        db_table = "instagram_comment"
        verbose_name = "Instagram-Comment"
        verbose_name_plural = "Instagram-Comments"
        ordering = ["-created_at"]

    post = models.ForeignKey(
        verbose_name="Instagram-Post",
        help_text="ID des Instagram-Posts",
        to=InstaPost,
        on_delete=models.CASCADE,
        related_name="comment_details",
        related_query_name="comment",
    )

    external_id = models.TextField(
        verbose_name="Externe ID",
        help_text="ID des Kommentars bei Instagram",
        unique=True,
    )

    created_at = models.DateTimeField(verbose_name="Erstellungszeitpunkt")

    is_account_answer = models.BooleanField(
        verbose_name="Antwort des Accounts",
        help_text="True für Antwort des Accounts, False für User*innen-Kommentar",
    )

    username = models.TextField(
        verbose_name="Username",
        help_text="Username der Kommentarverfasser*in",
        null=True,  # Werden wohl von Quintly nicht mehr geliefert
    )

    message_length = models.IntegerField(
        verbose_name="Kommentar-Länge",
        help_text="Zeichenzahl des Kommentars",
    )

    likes = models.IntegerField(
        verbose_name="Likes",
        help_text="Anzahl der Likes des Kommentars",
    )

    is_reply = models.BooleanField(
        verbose_name="Ist Antwort",
        help_text="True wenn Kommentar eine Antwort ist",
    )

    parent_comment_id = models.TextField(
        verbose_name="ID des Elternkommentars",
        help_text="ID des Kommentars, auf den sich die Antwort bezieht",
        null=True,
    )

    is_hidden = models.BooleanField(
        verbose_name="Ist verborgen",
        help_text="True wenn Kommentar verborgen wurde",
    )

    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.external_id} ({self.created_at})"


class InstaDemographics(models.Model):
    """Demographische Daten zu einzelnem Instagram Account."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_demographics"
        verbose_name = "Instagram Demographics"
        verbose_name_plural = "Instagram Demographics"
        unique_together = ("insta", "date", "age_range", "gender")
        ordering = ["-date"]

    class AgeRange(models.TextChoices):
        AGE_13_17 = "13-17", "13-17"
        AGE_18_24 = "18-24", "18-24"
        AGE_25_34 = "25-34", "25-34"
        AGE_35_44 = "35-44", "35-44"
        AGE_45_54 = "45-54", "45-54"
        AGE_55_64 = "55-64", "55-64"
        Age_65_PLUS = "65+", "65+"
        UNKNOWN = "unknown", "Unbekannt"

    class Gender(models.TextChoices):
        MALE = "male", "Männlich"
        FEMALE = "female", "Weiblich"
        UNKNOWN = "unknown", "Unbekannt"

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="instagram_demographics",
        related_query_name="instagram_demographics",
    )
    date = models.DateField(verbose_name="Datum")

    age_range = models.CharField(
        verbose_name="Altersgruppe",
        choices=AgeRange.choices,
        help_text="Die Altersgruppe, für die dieser Datenpunkt gilt.",
        max_length=20,
    )
    gender = models.CharField(
        verbose_name="Geschlecht",
        choices=Gender.choices,
        help_text="Das Geschlecht, für das dieser Datenpunkt gilt.",
        max_length=20,
    )
    followers = models.IntegerField(
        verbose_name="Followers",
        help_text="Anzahl der Followers dieser Demografie.",
        null=True,
    )
    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.insta.name} - {self.AgeRange(self.age_range).label}, {self.Gender(self.gender).label}"


class InstaHourlyFollowers(models.Model):
    """Daten zur Nutzung nach Tageszeit von einzelnem Instagram Account."""

    class Meta:
        """Model meta options."""

        db_table = "instagram_hourly_followers"
        verbose_name = "Instagram Hourly Followers"
        verbose_name_plural = "Instagram  Hourly Followers"
        unique_together = ("insta", "date_time")
        ordering = ["-date_time"]

    insta = models.ForeignKey(
        verbose_name="Instagram-Account",
        help_text="Globale ID des Instagram-Accounts",
        to=Insta,
        on_delete=models.CASCADE,
        related_name="instagram_hourly_followers",
        related_query_name="instagram_hourly_followers",
    )
    date_time = models.DateTimeField(
        verbose_name="Zeitpunkt",
        help_text="Datum und Uhrzeit des Datenpunktes",
    )
    followers = models.IntegerField(
        verbose_name="Followers",
        help_text="Anzahl der aktiven Follower",
    )
    quintly_last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated (Quintly)",
        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
        null=True,
    )
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.insta.name}: {self.date_time}"
