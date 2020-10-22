from django.db import models

from .base import Product


class Podcast(Product):
    class Meta:
        db_table = "podcast"
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"
        ordering = Product.Meta.ordering

    feed_url = models.URLField(max_length=1024, verbose_name="Feed-URL")
    author = models.CharField(max_length=200, verbose_name="Autor")
    image = models.URLField(max_length=1024, verbose_name="Bild")
    description = models.TextField(verbose_name="Beschreibung")

    spotify_id = models.CharField(
        max_length=32,
        verbose_name="Spotify ID",
        null=True,
    )

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)


class PodcastDataSpotify(models.Model):
    class Meta:
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
    listeners_all_time = models.IntegerField(verbose_name="Listeners (insgesamt)")
    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.podcast} - {self.date}"


class PodcastEpisode(models.Model):
    class Meta:
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

    spotify_id = models.CharField(
        max_length=32,
        verbose_name="Spotify ID",
        null=True,
    )

    duration = models.DurationField(verbose_name="Audio-Länge")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return (
            f"{self.podcast.name} - {self.title} ({self.publication_date_time.date()})"
        )


class PodcastEpisodeDataSpotify(models.Model):
    class Meta:
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
    class Meta:
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
    class Meta:
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
    class Meta:
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
        verbose_name="Hörzeit im Schnitt", help_text="HH:MM:SS"
    )
    quartile_1 = models.IntegerField(verbose_name="1. Quartil")
    quartile_2 = models.IntegerField(verbose_name="2. Quartil")
    quartile_3 = models.IntegerField(verbose_name="3. Quartil")
    complete = models.IntegerField(verbose_name="Komplett")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"
