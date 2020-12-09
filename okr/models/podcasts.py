"""Database models for podcasts."""

from django.db import models

from .base import Product


class Podcast(Product):
    """Enthält grundlegende Daten zu den einzelnen Podcast-Reihen, basierend auf Daten
    aus dem jeweiligen XML-Feed und von Spotify.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast"
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"
        ordering = Product.Meta.ordering

    feed_url = models.URLField(
        max_length=1024,
        verbose_name="Feed-URL",
        help_text="Adresse des RSS-Feeds des Podcasts",
        unique=True,
    )
    author = models.CharField(
        max_length=200,
        verbose_name="Autor*in",
        help_text="Autor*in des Podcasts",
    )
    image = models.URLField(
        max_length=1024,
        verbose_name="Bild",
        help_text="URL zum Coverbild des Podcasts",
    )
    description = models.TextField(
        verbose_name="Beschreibung", help_text="Beschreibungstext des Podcasts"
    )

    spotify_id = models.CharField(
        max_length=32,
        verbose_name="Spotify ID",
        help_text="Spotify ID, falls vorhanden",
        null=True,
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Datum der letzten Daten-Aktualisierung",
        auto_now=True,
    )


class PodcastDataSpotify(models.Model):
    """Daten zu Hörer*innen-Zahlen pro Podcast-Reihe, basierend auf Daten von Spotify.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_data_spotify"
        verbose_name = "Podcast-Spotify-Nutzer*innen"
        verbose_name_plural = "Podcast-Spotify-Nutzer*innen"
        ordering = ["-date", "podcast"]
        unique_together = ["date", "podcast"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Erstellungsdatum des Datenpunkts",
    )
    podcast = models.ForeignKey(
        verbose_name="Podcast ID",
        to=Podcast,
        on_delete=models.CASCADE,
        related_name="data_spotify",
        related_query_name="data_spotify",
        help_text="Globale ID der Podcast-Reihe",
    )
    followers = models.IntegerField(
        verbose_name="Follower",
        help_text="Anzahl der Followers des Podcasts",
    )
    listeners = models.IntegerField(
        verbose_name="Listeners",
        help_text="Anzahl der Hörer*innen",
    )
    listeners_weekly = models.IntegerField(
        verbose_name="Listeners (wöchentlich)",
        help_text="Hörer*innen pro Woche",
    )
    listeners_monthly = models.IntegerField(
        verbose_name="Listeners (monatlich)",
        help_text="Hörer*innen pro Monat",
    )
    listeners_all_time = models.IntegerField(
        verbose_name="Listeners (insgesamt)",
        help_text="Hörer*innen insgesamt",
    )
    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Datum der letzten Daten-Aktualisierung",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.podcast} - {self.date}"


class PodcastDataSpotifyHourly(models.Model):
    """Daten über die stündliche Nutzung der Podcast-Reihen, die auf Spotify verfügbar
    sind.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_data_spotify_hourly"
        verbose_name = "Podcast-Spotify-Abruf (stündlich)"
        verbose_name_plural = "Podcast-Spotify-Abrufe (stündlich)"
        ordering = ["-date_time", "podcast"]
        unique_together = ["date_time", "podcast"]

    date_time = models.DateTimeField(
        verbose_name="Zeitpunkt",
        help_text="Datum und Uhrzeit des Datenpunktes",
    )
    podcast = models.ForeignKey(
        verbose_name="Podcast",
        to=Podcast,
        on_delete=models.CASCADE,
        related_name="data_spotify_hourly",
        related_query_name="data_spotify_hourly",
        help_text="Globale ID der Podcast-Reihe",
    )
    starts = models.IntegerField(
        verbose_name="Starts",
        help_text="Anzahl der Starts",
    )
    streams = models.IntegerField(
        verbose_name="Streams",
        help_text="Anzahl der Streams",
    )

    def __str__(self):
        return f"{self.podcast} - {self.date_time}"


class PodcastEpisode(models.Model):
    """Daten zu den einzelnen Folgen der Podcasts, basierend auf Daten aus dem XML-Feed
    und von Spotify.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_episode"
        verbose_name = "Podcast-Episode"
        verbose_name_plural = "Podcast-Episoden"
        ordering = ["-publication_date_time"]

    title = models.CharField(
        max_length=400,
        verbose_name="Titel",
        help_text="Titel der einzelnen Folge",
    )
    podcast = models.ForeignKey(
        verbose_name="Podcast",
        to=Podcast,
        on_delete=models.CASCADE,
        related_name="episodes",
        related_query_name="episode",
        help_text="Globale ID der Podcast-Reihe",
    )
    description = models.TextField(
        verbose_name="Beschreibung",
        help_text="Beschreibungstext der Folge",
    )
    publication_date_time = models.DateTimeField(
        verbose_name="Datum",
        help_text="Veröffentlichungsdatum der Folge",
    )
    media = models.URLField(
        max_length=1024,
        verbose_name="Media-URL",
        help_text="URL der Mediendatei",
    )
    zmdb_id = models.IntegerField(
        verbose_name="ZMDB-ID",
        help_text="ZMDB ID der Mediendatei",
        unique=True,
    )

    spotify_id = models.CharField(
        max_length=32,
        verbose_name="Spotify ID",
        help_text="Spotify ID, falls vorhanden",
        null=True,
    )

    duration = models.DurationField(
        verbose_name="Länge",
        help_text="Länge der Mediendatei",
    )

    available = models.BooleanField(
        verbose_name="Verfügbar",
        help_text="Indikator, ob diese Episode momentan im Feed verfügbar ist",
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Letzte Aktualisierung des Datenpunktes",
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.podcast.name} - {self.title} ({self.publication_date_time.date()})"
        )


class PodcastEpisodeDataSpotify(models.Model):
    """Zusätzliche Daten zu einzelnen Podcast-Folgen. Nur für Podcasts, die auf Spotify
    verfügbar sind.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_episode_data_spotify"
        verbose_name = "Podcast-Episoden-Abruf (Spotify)"
        verbose_name_plural = "Podcast-Episoden-Abrufe (Spotify)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der Abrufzahlen",
    )
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_spotify",
        related_query_name="data_spotify",
        help_text="Globale ID der Episode",
    )
    starts = models.IntegerField(
        verbose_name="Starts",
        help_text="Anzahl der Starts",
    )
    streams = models.IntegerField(
        verbose_name="Streams",
        help_text="Anzahl der Streams",
    )
    listeners = models.IntegerField(
        verbose_name="Listeners",
        help_text="Hörer*innen für den jeweiligen Tag",
    )
    listeners_all_time = models.IntegerField(
        verbose_name="Listeners (insgesamt)",
        help_text="Gesamtzahl der Hörer*innen",
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Zeitpunkt der Datenaktualisierung",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataSpotifyUser(models.Model):
    """Enthält demographische Daten von Spotify zu den auf Spotify verfügbaren Folgen.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_episode_data_spotify_user"
        verbose_name = "Podcast-Episoden-Nutzer (Spotify)"
        verbose_name_plural = "Podcast-Episoden-Nutzer (Spotify)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der Abrufzahlen",
    )
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_spotify_user",
        related_query_name="data_spotify_user",
        help_text="Globale ID der Episode",
    )
    age_0_17 = models.IntegerField(
        verbose_name="0-17",
        help_text="Hörer*innen zwischen 0 und 17",
    )
    age_18_22 = models.IntegerField(
        verbose_name="18-22",
        help_text="Hörer*innen zwischen 18 und 22",
    )
    age_23_27 = models.IntegerField(
        verbose_name="23-27",
        help_text="Hörer*innen zwischen 23 und 27",
    )
    age_28_34 = models.IntegerField(
        verbose_name="28-34",
        help_text="Hörer*innen zwischen 28 und 34",
    )
    age_35_44 = models.IntegerField(
        verbose_name="35-44",
        help_text="Hörer*innen zwischen 35 und 44",
    )
    age_45_59 = models.IntegerField(
        verbose_name="45-59",
        help_text="Hörer*innen zwischen 45 und 59",
    )
    age_60_150 = models.IntegerField(
        verbose_name="60-150",
        help_text="Hörer*innen zwischen 60 und 150",
    )
    age_unknown = models.IntegerField(
        verbose_name="Unbekannt",
        help_text="Hörer*innen ohne Altersangabe",
    )
    gender_female = models.IntegerField(
        verbose_name="Weiblich",
        help_text="Anzahl der Hörerinnen",
    )
    gender_male = models.IntegerField(
        verbose_name="Männlich",
        help_text="Anzahl der Hörer",
    )
    gender_non_binary = models.IntegerField(
        verbose_name="Non_binary",
        help_text="Anzahl der non-binary Hörer*innen",
    )
    gender_not_specified = models.IntegerField(
        verbose_name="Nicht angegeben",
        help_text="Hörer*innen ohne Geschlechtsangabe",
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Zeitpunkt der Datenaktualisierung",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataSpotifyDemographics(models.Model):
    """Enthält demographische Daten von Spotify zu den auf Spotify verfügbaren Folgen.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_episode_data_spotify_demographics"
        verbose_name = "Podcast-Episoden-Demografiedaten (Spotify)"
        verbose_name_plural = "Podcast-Episoden-Demografiedaten (Spotify)"
        unique_together = ("date", "episode", "age_range", "gender")
        ordering = ["-date", "episode"]

    class AgeRange(models.TextChoices):
        AGE_0_17 = "0-17", "0-17"
        AGE_18_22 = "18-22", "18-22"
        AGE_23_27 = "23-27", "23-27"
        AGE_28_34 = "28-34", "28-34"
        AGE_35_44 = "35-44", "35-44"
        AGE_45_59 = "45-59", "45-59"
        AGE_60_150 = "60-150", "60-150"
        UNKNOWN = "unknown", "Unbekannt"

    class Gender(models.TextChoices):
        NOT_SPECIFIED = "NOT_SPECIFIED", "Nicht Angegeben"
        MALE = "MALE", "Männlich"
        FEMALE = "FEMALE", "Weiblich"
        NON_BINARY = "NON_BINARY", "Non-Binary"

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der Abrufzahlen",
    )
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_spotify_demographics",
        related_query_name="data_spotify_demographics",
        help_text="Globale ID der Episode",
    )

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
    count = models.IntegerField(
        verbose_name="Streams",
        help_text="Anzahl der Streams dieser Demografie.",
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Zeitpunkt der Datenaktualisierung",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.episode.title}: {self.AgeRange(self.age_range).label} - {self.AgeRange(self.age_range).label}"


class PodcastEpisodeDataPodstat(models.Model):
    """Hörer*innenzahlen einzelner Podcast-Folgen, basierend auf Daten von
        Podstat/Spotify.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_episode_data_podstat"
        verbose_name = "Podcast-Episoden-Abruf (Podstat)"
        verbose_name_plural = "Podcast-Episoden-Abrufe (Podstat)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der Abrufzahlen",
    )
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_podstat",
        related_query_name="data_podstat",
        help_text="Globale ID der Episode",
    )
    downloads = models.IntegerField(
        verbose_name="Downloads",
        help_text="Anzahl der Downloads",
    )
    ondemand = models.IntegerField(
        verbose_name="OnDemand",
        help_text="Anzahl der Ondemand-Abrufe",
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Zeitpunkt der Datenaktualisierung",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataSpotifyPerformance(models.Model):
    """Performance-Daten zu den auf Spotify verfügbaren Folgen.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_episode_data_spotify_performance"
        verbose_name = "Podcast-Episoden-Performance (Spotify)"
        verbose_name_plural = "Podcast-Episoden-Performance (Spotify)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der Performance-Daten",
    )
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_spotify_performance",
        related_query_name="data_spotify_performance",
        help_text="Globale ID der Episode",
    )
    average_listen = models.DurationField(
        verbose_name="Average Listen",
        help_text="HH:MM:SS, 50% der Listeners hörten bis zu diesem Zeitpunkt.",
    )
    quartile_1 = models.IntegerField(
        verbose_name="1. Quartil",
        help_text="Hörer*innen im 1. Viertel der Folge",
    )
    quartile_2 = models.IntegerField(
        verbose_name="2. Quartil",
        help_text="Hörer*innen im 2. Viertel der Folge",
    )
    quartile_3 = models.IntegerField(
        verbose_name="3. Quartil",
        help_text="Hörer*innen im 3. Viertel der Folge",
    )
    complete = models.IntegerField(
        verbose_name="Komplett",
        help_text="	Hörer*innen der gesamten Folge",
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Zeitpunkt der Datenaktualisierung",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataWebtrekkPerformance(models.Model):
    """Zusätzliche Abruf-Daten von Webtrekk für die einzelnen Folgen.
    """

    class Meta:
        """Model meta options."""

        db_table = "podcast_episode_data_webtrekk_performance"
        verbose_name = "Podcast-Episoden-Performance (Webtrekk)"
        verbose_name_plural = "Podcast-Episoden-Performance (Webtrekk)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(
        verbose_name="Datum",
        help_text="Datum der Performance-Daten",
    )
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_webtrekk_performance",
        related_query_name="data_webtrekk_performance",
        help_text="Globale ID der Episode",
    )

    media_views = models.IntegerField(
        verbose_name="Angefangen",
        help_text="Angefangene Abrufe der Mediendatei",
    )
    media_views_complete = models.IntegerField(
        verbose_name="Vollständig",
        help_text="Abgeschlossene Abrufe der Mediendatei",
    )
    playing_time = models.DurationField(
        verbose_name="Spieldauer", help_text="Abspieldauer der Mediendatei (HH:MM:SS)"
    )

    last_updated = models.DateTimeField(
        verbose_name="Zuletzt upgedated",
        help_text="Zeitpunkt der Datenaktualisierung",
        auto_now=True,
    )

    def __str__(self):
        return f"{self.episode.title} ({self.date})"
