# Generated by Django 3.2.3 on 2021-06-16 19:52

import datetime as dt
from time import sleep

from django.db import migrations, models
from django.db.models.aggregates import Sum
import django.db.models.deletion
from loguru import logger


def translate_spotify_demographic_data(apps, schema_editor):
    Podcast = apps.get_model("okr", "Podcast")
    PodcastEpisode = apps.get_model("okr", "PodcastEpisode")

    PodcastEpisodeDataSpotifyDemographics = apps.get_model(
        "okr", "PodcastEpisodeDataSpotifyDemographics"
    )
    PodcastDataSpotifyDemographics = apps.get_model(
        "okr", "PodcastDataSpotifyDemographics"
    )

    if Podcast.objects.all().count() == 0:
        return

    translate_podcasts(
        Podcast,
        PodcastEpisodeDataSpotifyDemographics,
        PodcastDataSpotifyDemographics,
    )

    translate_episodes(PodcastEpisode, PodcastEpisodeDataSpotifyDemographics)

    # Clean up other messes
    PodcastEpisodeDataSpotifyDemographics.objects.filter(
        episode__spotify_id=None,
    ).delete()

    # Just... wait a bit and do it again and wait some more to hopefully fix migration
    sleep(10)
    translate_episodes(PodcastEpisode, PodcastEpisodeDataSpotifyDemographics)
    sleep(30)


def translate_podcasts(
    Podcast, PodcastEpisodeDataSpotifyDemographics, PodcastDataSpotifyDemographics
):
    logger.info("Filling PodcastDataSpotifyDemographics...")

    for podcast in Podcast.objects.exclude(spotify_id=None):
        podcast_data = (
            PodcastEpisodeDataSpotifyDemographics.objects.values(
                "date", "age_range", "gender"
            )
            .order_by("-date")
            .annotate(count=models.Sum("count"))
            .filter(episode__podcast=podcast)
        )

        objs = PodcastDataSpotifyDemographics.objects.bulk_create(
            [
                PodcastDataSpotifyDemographics(**data, podcast=podcast)
                for data in podcast_data
            ],
            batch_size=500,
        )

        logger.info(f"{len(objs)} for {podcast.name}")
        del podcast_data
        del objs

    logger.success("Filling PodcastDataSpotifyDemographics done!")


def translate_episodes(PodcastEpisode, PodcastEpisodeDataSpotifyDemographics):
    logger.info("Aggregating PodcastEpisodeDataSpotifyDemographics...")
    dummy_date = dt.date.today()

    for episode in PodcastEpisode.objects.exclude(spotify_id=None):
        episode_data = list(
            PodcastEpisodeDataSpotifyDemographics.objects.values("age_range", "gender")
            .order_by("-episode__published_date_time")
            .annotate(count=Sum("count"))
            .filter(episode=episode)
        )

        # Delete all before we create the new, aggregated one
        PodcastEpisodeDataSpotifyDemographics.objects.filter(episode=episode).delete()

        objs = PodcastEpisodeDataSpotifyDemographics.objects.bulk_create(
            [
                PodcastEpisodeDataSpotifyDemographics(
                    **data, episode=episode, date=dummy_date
                )
                for data in episode_data
            ],
            batch_size=500,
        )

        logger.info(f"{len(objs)} for {episode.title}")
        del episode_data
        del objs

    logger.success("Aggregating PodcastEpisodeDataSpotifyDemographics done!")


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("okr", "0063_cachedwebtrekkrequest"),
    ]

    operations = [
        migrations.CreateModel(
            name="PodcastDataSpotifyDemographics",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date",
                    models.DateField(
                        help_text="Datum der Abrufzahlen", verbose_name="Datum"
                    ),
                ),
                (
                    "age_range",
                    models.CharField(
                        choices=[
                            ("0-17", "0-17"),
                            ("18-22", "18-22"),
                            ("23-27", "23-27"),
                            ("28-34", "28-34"),
                            ("35-44", "35-44"),
                            ("45-59", "45-59"),
                            ("60-150", "60-150"),
                            ("unknown", "Unbekannt"),
                        ],
                        help_text="Die Altersgruppe, für die dieser Datenpunkt gilt.",
                        max_length=20,
                        verbose_name="Altersgruppe",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("NOT_SPECIFIED", "Nicht Angegeben"),
                            ("MALE", "Männlich"),
                            ("FEMALE", "Weiblich"),
                            ("NON_BINARY", "Non-Binary"),
                        ],
                        help_text="Das Geschlecht, für das dieser Datenpunkt gilt.",
                        max_length=20,
                        verbose_name="Geschlecht",
                    ),
                ),
                (
                    "count",
                    models.IntegerField(
                        help_text="Anzahl der Streams dieser Demografie.",
                        verbose_name="Streams",
                    ),
                ),
                (
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Zeitpunkt der Datenaktualisierung",
                        verbose_name="Zuletzt upgedated",
                    ),
                ),
                (
                    "podcast",
                    models.ForeignKey(
                        help_text="Globale ID des Podcasts",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_spotify_demographics",
                        related_query_name="data_spotify_demographics",
                        to="okr.podcast",
                        verbose_name="Podcast",
                    ),
                ),
            ],
            options={
                "verbose_name": "Podcast-Demografiedaten (Spotify)",
                "verbose_name_plural": "Podcast-Demografiedaten (Spotify)",
                "db_table": "podcast_data_spotify_demographics",
                "ordering": ["-date", "podcast"],
                "unique_together": {("date", "podcast", "age_range", "gender")},
            },
        ),
        migrations.RunPython(translate_spotify_demographic_data),
        migrations.AlterModelOptions(
            name="podcastepisodedataspotifydemographics",
            options={
                "ordering": ["episode__podcast", "episode"],
                "verbose_name": "Podcast-Episoden-Demografiedaten (Spotify)",
                "verbose_name_plural": "Podcast-Episoden-Demografiedaten (Spotify)",
            },
        ),
        migrations.AlterUniqueTogether(
            name="podcastepisodedataspotifydemographics",
            unique_together={("episode", "age_range", "gender")},
        ),
        migrations.RemoveField(
            model_name="podcastepisodedataspotifydemographics",
            name="date",
        ),
    ]
