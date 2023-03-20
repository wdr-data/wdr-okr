# Generated by Django 3.1.2 on 2020-10-23 12:36

from django.db import migrations, models
import django.db.models.deletion


def scrape_spotify_api_last_days(apps, schema_editor):
    PodcastDataSpotify = apps.get_model("okr", "PodcastDataSpotify")

    if PodcastDataSpotify.objects.count() == 0:
        return

    from okr.scrapers.podcasts import scrape_spotify_api

    scrape_spotify_api()


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0023_auto_20201023_1207"),
    ]

    operations = [
        migrations.CreateModel(
            name="PodcastDataSpotifyHourly",
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
                ("date_time", models.DateTimeField(verbose_name="Zeitpunkt")),
                ("starts", models.IntegerField(verbose_name="Starts")),
                ("streams", models.IntegerField(verbose_name="Streams")),
                (
                    "podcast",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_spotify_hourly",
                        related_query_name="data_spotify_hourly",
                        to="okr.podcast",
                        verbose_name="Podcast",
                    ),
                ),
            ],
            options={
                "verbose_name": "Podcast-Spotify-Abruf (stündlich)",
                "verbose_name_plural": "Podcast-Spotify-Abrufe (stündlich)",
                "db_table": "podcast_data_spotify_hourly",
                "ordering": ["-date_time", "podcast"],
                "unique_together": {("date_time", "podcast")},
            },
        ),
        migrations.RunPython(scrape_spotify_api_last_days),
    ]
