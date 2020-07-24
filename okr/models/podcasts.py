from django.db import models
from .base import Product


class Podcast(Product):
    class Meta:
        verbose_name = "Podcast"
        verbose_name_plural = "Podcasts"
        ordering = Product.Meta.ordering

    feed_url = models.URLField(max_length=1024, verbose_name="Feed-URL")
    author = models.CharField(max_length=200, verbose_name="Autor")
    image = models.URLField(max_length=1024, verbose_name="Bild")
    description = models.TextField(verbose_name="Beschreibung")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)


class PodcastDataSpotifyFollowers(models.Model):
    class Meta:
        verbose_name = "Podcast-Spotify-Follower"
        verbose_name_plural = "Podcast-Spotify-Follower"
        ordering = ["-date", "podcast"]

    date = models.DateField(verbose_name="Datum")
    podcast = models.ForeignKey(
        verbose_name="Podcast",
        to=Podcast,
        on_delete=models.CASCADE,
        related_name="followers",
        related_query_name="followers",
    )
    followers = models.IntegerField(verbose_name="Follower")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.podcast} - {self.date}"


class PodcastEpisode(models.Model):
    class Meta:
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
    duration = models.DurationField(verbose_name="Audio-Länge")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return (
            f"{self.podcast.name} - {self.title} ({self.publication_date_time.date()})"
        )


class PodcastEpisodeDataSpotify(models.Model):
    class Meta:
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
    listeners = models.IntegerField(verbose_name="Hörer")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataSpotifyUser(models.Model):
    class Meta:
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


class PodcastEpisodeDataPodstatDownload(models.Model):
    class Meta:
        verbose_name = "Podcast-Episoden-Downloads (Podstat)"
        verbose_name_plural = "Podcast-Episoden-Downloads (Podstat)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(verbose_name="Datum")
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_podstat_download",
        related_query_name="data_podstat_download",
    )
    nv = models.IntegerField(verbose_name="Nutzungsvorgang")
    nv10 = models.IntegerField(verbose_name="Nutzungsvorgang über 10 Sec.")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataPodstatOndemand(models.Model):
    class Meta:
        verbose_name = "Podcast-Episoden-Streams (Podstat)"
        verbose_name_plural = "Podcast-Episoden-Streams (Podstat)"
        unique_together = ("date", "episode")
        ordering = ["-date", "episode"]

    date = models.DateField(verbose_name="Datum")
    episode = models.ForeignKey(
        verbose_name="Episode",
        to=PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="data_podstat_ondemand",
        related_query_name="data_podstat_ondemand",
    )
    nv = models.IntegerField(verbose_name="Nutzungsvorgang")
    nv10 = models.IntegerField(verbose_name="Nutzungsvorgang über 10 Sec.")

    last_updated = models.DateTimeField(verbose_name="Zuletzt upgedated", auto_now=True)

    def __str__(self):
        return f"{self.episode.title} ({self.date})"


class PodcastEpisodeDataSpotifyPerformance(models.Model):
    class Meta:
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
