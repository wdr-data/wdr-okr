# Generated by Django 3.2.9 on 2021-11-24 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0079_instavideodata"),
    ]

    operations = [
        migrations.AlterField(
            model_name="youtubetrafficsource",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("advertising", "Werbung"),
                    ("annotation", "Annotation"),
                    ("campaign_card", "Kampagnenkarte"),
                    ("end_screen", "Endscreen"),
                    ("ext_url", "Externe URL"),
                    ("no_link_embedded", "Kein Link (eingebettet)"),
                    ("no_link_other", "Kein Link (sonstiges)"),
                    ("notification", "Benachrichtigung"),
                    ("playlist", "Playlist"),
                    ("promoted", "Promoted"),
                    ("related_video", "Related"),
                    ("shorts", "Shorts"),
                    ("sound_page", "Soundpage"),
                    ("subscriber", "Abonnent*in"),
                    ("yt_channel", "Youtube-Kanal"),
                    ("yt_other_page", "Sonstige Youtube-Seite"),
                    ("yt_playlist_page", "Youtube Playlist-Seite"),
                    ("yt_search", "Youtube-Suche"),
                    ("hashtags", "Hashtags"),
                ],
                max_length=40,
                verbose_name="Source Type",
            ),
        ),
        migrations.CreateModel(
            name="YouTubeVideoAnalyticsExtra",
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
                ("date", models.DateField(verbose_name="Datum")),
                (
                    "impressions",
                    models.IntegerField(verbose_name="Impressions"),
                ),
                ("clicks", models.IntegerField(verbose_name="Clicks")),
                (
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Zuletzt upgedated"
                    ),
                ),
                (
                    "youtube_video",
                    models.ForeignKey(
                        help_text="ID des YouTube-Videos",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analytics_extra",
                        related_query_name="analytics_extra",
                        to="okr.youtubevideo",
                        verbose_name="YouTube-Video",
                    ),
                ),
            ],
            options={
                "verbose_name": "YouTube Video Analytics Extra",
                "verbose_name_plural": "YouTube Video Analytics Extra",
                "db_table": "youtube_video_analytics_extra",
                "ordering": ["-date"],
                "unique_together": {("youtube_video", "date")},
            },
        ),
    ]
