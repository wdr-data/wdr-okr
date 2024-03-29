# Generated by Django 3.2.15 on 2022-09-05 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0083_alter_youtubevideodemographics_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="instapost",
            name="shares",
            field=models.IntegerField(
                help_text="Organische Shares, nur für Reels verfügbar",
                null=True,
                verbose_name="Shares",
            ),
        ),
        migrations.CreateModel(
            name="InstaReelData",
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
                        help_text="Datum des Datenpunkts", verbose_name="Datum"
                    ),
                ),
                (
                    "comments",
                    models.IntegerField(
                        help_text="Anzahl der Kommentare",
                        null=True,
                        verbose_name="Kommentare",
                    ),
                ),
                (
                    "likes",
                    models.IntegerField(
                        help_text="Anzahl der Likes", null=True, verbose_name="Likes"
                    ),
                ),
                ("reach", models.IntegerField(null=True, verbose_name="Reichweite")),
                (
                    "saved",
                    models.IntegerField(
                        help_text="Anzahl der Saves", null=True, verbose_name="Saves"
                    ),
                ),
                (
                    "video_views",
                    models.IntegerField(
                        help_text="Video-Views (3 sec oder mehr)",
                        null=True,
                        verbose_name="Video-Views",
                    ),
                ),
                (
                    "shares",
                    models.IntegerField(
                        help_text="Organische Shares", null=True, verbose_name="Shares"
                    ),
                ),
                (
                    "quintly_last_updated",
                    models.DateTimeField(
                        help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
                        null=True,
                        verbose_name="Zuletzt upgedated (Quintly)",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        help_text="Globale ID des Posts",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reel_data",
                        related_query_name="reel_data",
                        to="okr.instapost",
                        verbose_name="Post",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instagram Reel-Daten",
                "verbose_name_plural": "Instagram Reel-Daten",
                "db_table": "instagram_reel_data",
                "ordering": ["-date"],
                "unique_together": {("post", "date")},
            },
        ),
    ]
