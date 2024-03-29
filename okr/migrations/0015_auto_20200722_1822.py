# Generated by Django 3.0.8 on 2020-07-22 16:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0014_auto_20200722_1703"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="podcastdataspotifyfollowers",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="podcastepisode",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="podcastepisodedatapodstatdownload",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="podcastepisodedatapodstatondemand",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="podcastepisodedataspotify",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="podcastepisodedataspotifyperformance",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="podcastepisodedataspotifyuser",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
    ]
