""" Database models for podcasts
"""

from django.db import models

from .base import Product


class Podcast(Product):
    """ Individual Podcast series, based on data from XML feed.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast"
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"
        ordering = Product.Meta.ordering

    feed_url = models.URLField(max_length=1024, verbose_name="Feed-URL", unique=True)
    author = models.CharField(max_length=200, verbose_name="Autor")
    image = models.URLField(max_length=1024, verbose_name="Bild")
    description = models.TextField(verbose_name="Beschreibung")

    spotify_id = models.CharField(max_length=32, verbose_name="Spotify ID", null=True)

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)


class PodcastDataSpotify(models.Model):
    """ Individual Podcast series, based on data from Spotify.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast_data_spotify"
        verbose_name = "Podcast-Spotify-Nutzer"
        verbose_name_plural = "Podcast-Spotify-Nutzer"
        ordering = ["-date", "podcast"]
        unique_together = ["date", "podcast"]

    date = models.DateField(verbose_name="Datum")
    podcast = models.ForeignKey(
        verbose_name="Podcast",
        to=Podcast,
        on_delete=models.CASCADE,
        related_name="data_spotify",
        related_query_name="data_spotify",
    )
    followers = models.IntegerField(verbose_name="Follower")
    listeners = models.IntegerField(verbose_name="Listeners")
    listeners_weekly = models.IntegerField(verbose_name="Listeners (wöchentlich)")
    listeners_monthly = models.IntegerField(verbose_name="Listeners (monatlich)")
    listeners_all_time = models.IntegerField(verbose_name="Listeners (insgesamt)")
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.podcast} - {self.date}"


class PodcastDataSpotifyHourly(models.Model):
    """ Individual Podcast series, based on hourly Spotify data.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast_data_spotify_hourly"
        verbose_name = "Podcast-Spotify-Abruf (stündlich)"
        verbose_name_plural = "Podcast-Spotify-Abrufe (stündlich)"
        ordering = ["-date_time", "podcast"]
        unique_together = ["date_time", "podcast"]

    date_time = models.DateTimeField(verbose_name="Zeitpunkt")
    podcast = models.ForeignKey(
        verbose_name="Podcast",
        to=Podcast,
        on_delete=models.CASCADE,
        related_name="data_spotify_hourly",
        related_query_name="data_spotify_hourly",
    )
    starts = models.IntegerField(verbose_name="Starts")
    streams = models.IntegerField(verbose_name="Streams")

    def __str__(self):
        return f"{self.podcast} - {self.date_time}"


class PodcastEpisode(models.Model):
    """ Individual Podcast episodes, based on data from XML feed.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast_episode"
        verbose_name = "Podcast-Episode"
        verbose_name_plural = "Podcast-Episoden"
        ordering = ["-publication_date_time"]

    title = models.CharField(max_length=400, verbose_name="Titel")
    podcast = models.ForeignKey(
        verbose_name="Podcast",
        to=Podcast,
        on_delete=models.CASCADE,
        related_name="episodes",
        related_query_name="episode",
    )
    description = models.TextField(verbose_name="Beschreibung")
    publication_date_time = models.DateTimeField(verbose_name="Veröffentlicht am")
    media = models.URLField(max_length=1024, verbose_name="Media-URL")
    zmdb_id = models.IntegerField(verbose_name="ZMDB-ID", unique=True)

    spotify_id = models.CharField(max_length=32, verbose_name="Spotify ID", null=True)

    duration = models.DurationField(verbose_name="Audio-Länge")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return (
            f"{self.podcast.name} - {self.title} ({self.publication_date_time.date()})"
        )


class PodcastEpisodeDataSpotify(models.Model):
    """ Individual Podcast episodes, based on data from Spotify.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast_episode_data_spotify"
        verbose_name = "Podcast-Episoden-Abruf (Spotify)"
        verbose_name_plural = "Podcast-Episoden-Abrufe (Spotify)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(verbose_name="Datum")
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_spotify",
        related_query_name="data_spotify",
    )
    starts = models.IntegerField(verbose_name="Starts")
    streams = models.IntegerField(verbose_name="Streams")
    listeners = models.IntegerField(verbose_name="Listeners")
    listeners_all_time = models.IntegerField(verbose_name="Listeners (insgesamt)")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataSpotifyUser(models.Model):
    """ User data for individual Podcast episodes, based on data from Spotify.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast_episode_data_spotify_user"
        verbose_name = "Podcast-Episoden-Nutzer (Spotify)"
        verbose_name_plural = "Podcast-Episoden-Nutzer (Spotify)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(verbose_name="Datum")
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_spotify_user",
        related_query_name="data_spotify_user",
    )
    age_0_17 = models.IntegerField(verbose_name="0-17 Jahre")
    age_18_22 = models.IntegerField(verbose_name="18-22 Jahre")
    age_23_27 = models.IntegerField(verbose_name="23-27 Jahre")
    age_28_34 = models.IntegerField(verbose_name="28-34 Jahre")
    age_35_44 = models.IntegerField(verbose_name="35-44 Jahre")
    age_45_59 = models.IntegerField(verbose_name="45-59 Jahre")
    age_60_150 = models.IntegerField(verbose_name="60-150 Jahre")
    age_unknown = models.IntegerField(verbose_name="Unbekanntes Alter")
    gender_female = models.IntegerField(verbose_name="Weiblich")
    gender_male = models.IntegerField(verbose_name="Männlich")
    gender_non_binary = models.IntegerField(verbose_name="Non_binary")
    gender_not_specified = models.IntegerField(
        verbose_name="Geschlecht nicht angegeben"
    )

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataPodstat(models.Model):
    """Individual Podcast episodes, based on data from Podstat.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast_episode_data_podstat"
        verbose_name = "Podcast-Episoden-Abruf (Podstat)"
        verbose_name_plural = "Podcast-Episoden-Abrufe (Podstat)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(verbose_name="Datum")
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_podstat",
        related_query_name="data_podstat",
    )
    downloads = models.IntegerField(verbose_name="Downloads")
    ondemand = models.IntegerField(verbose_name="OnDemand")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataSpotifyPerformance(models.Model):
    """ Performance data for individual Podcast episodes, based on Spotify data.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast_episode_data_spotify_performance"
        verbose_name = "Podcast-Episoden-Performance (Spotify)"
        verbose_name_plural = "Podcast-Episoden-Performance (Spotify)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(verbose_name="Datum")
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_spotify_performance",
        related_query_name="data_spotify_performance",
    )
    average_listen = models.DurationField(
        verbose_name="Average Listen",
        help_text="HH:MM:SS, 50% der Listeners hörten bis zu diesem Zeitpunkt.",
    )
    quartile_1 = models.IntegerField(verbose_name="1. Quartil")
    quartile_2 = models.IntegerField(verbose_name="2. Quartil")
    quartile_3 = models.IntegerField(verbose_name="3. Quartil")
    complete = models.IntegerField(verbose_name="Komplett")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataWebtrekkPerformance(models.Model):
    """ Performance data for individual Podcast episodes, based on Webtrekk data.
    """

    class Meta:
        """ Model meta options.
        """

        db_table = "podcast_episode_data_webtrekk_performance"
        verbose_name = "Podcast-Episoden-Performance (Webtrekk)"
        verbose_name_plural = "Podcast-Episoden-Performance (Webtrekk)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(verbose_name="Datum")
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_webtrekk_performance",
        related_query_name="data_webtrekk_performance",
    )

    media_views = models.IntegerField(verbose_name="Medienansichten")
    media_views_complete = models.IntegerField(
        verbose_name="Medienansichten vollständig"
    )
    playing_time = models.DurationField(verbose_name="Spieldauer", help_text="HH:MM:SS")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"
