# Generated by Django 3.1.2 on 2020-10-21 14:55
import functools

from django.db import migrations, models


def fill_spotify_ids(apps, schema_editor):
    Podcast = apps.get_model("okr", "Podcast")

    if Podcast.objects.all().count() == 0:
        return

    from okr.scrapers.podcasts.spotify_api import spotify_api, fetch_all
    from okr.scrapers.podcasts import scrape_feed

    licensed_podcasts = spotify_api.licensed_podcasts()
    spotify_podcasts = fetch_all(
        functools.partial(spotify_api.shows, market="DE"),
        list(
            uri.replace("spotify:show:", "")
            for uri in licensed_podcasts["shows"].keys()
        ),
        "shows",
    )
    spotify_podcasts = {p["name"]: p for p in spotify_podcasts}

    for podcast in Podcast.objects.all():
        if podcast.name in spotify_podcasts:
            podcast.spotify_id = spotify_podcasts[podcast.name]["id"]
            podcast.save()

    scrape_feed()


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0019_podcastepisodedatapodstat"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="spotify_id",
            field=models.CharField(max_length=32, null=True, verbose_name="Spotify ID"),
        ),
        migrations.AddField(
            model_name="podcastepisode",
            name="spotify_id",
            field=models.CharField(max_length=32, null=True, verbose_name="Spotify ID"),
        ),
        migrations.RunPython(fill_spotify_ids),
    ]
