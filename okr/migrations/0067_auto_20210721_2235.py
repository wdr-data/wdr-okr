# Generated by Django 3.2.4 on 2021-07-21 20:35

from time import sleep

from django.db import migrations, models
import django.db.models.deletion


def delete_non_daily_intervals(apps, schema_editor):
    InstaInsight = apps.get_model("okr", "InstaInsight")

    if InstaInsight.objects.all().count() == 0:
        return

    InstaInsight.objects.exclude(interval="daily").delete()
    sleep(5)


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0066_auto_20210719_1622"),
    ]

    operations = [
        migrations.RunPython(delete_non_daily_intervals),
        migrations.CreateModel(
            name="InstaDemographics",
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
                    "age_range",
                    models.CharField(
                        choices=[
                            ("13-17", "13-17"),
                            ("18-24", "18-24"),
                            ("25-34", "25-34"),
                            ("35-44", "35-44"),
                            ("45-54", "45-54"),
                            ("55-64", "55-64"),
                            ("65+", "65+"),
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
                            ("male", "Männlich"),
                            ("female", "Weiblich"),
                            ("unknown", "Unbekannt"),
                        ],
                        help_text="Das Geschlecht, für das dieser Datenpunkt gilt.",
                        max_length=20,
                        verbose_name="Geschlecht",
                    ),
                ),
                (
                    "followers",
                    models.IntegerField(
                        help_text="Anzahl der Followers dieser Demografie.",
                        null=True,
                        verbose_name="Followers",
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
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Zuletzt upgedated"
                    ),
                ),
                (
                    "insta",
                    models.ForeignKey(
                        help_text="Globale ID des Instagram-Accounts",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instagram_demographics",
                        related_query_name="instagram_demographics",
                        to="okr.insta",
                        verbose_name="Instagram-Account",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instagram Demographics",
                "verbose_name_plural": "Instagram Demographics",
                "db_table": "instagram_demographics",
                "ordering": ["-date"],
                "unique_together": {("insta", "date", "age_range", "gender")},
            },
        ),
        migrations.CreateModel(
            name="InstaHourlyFollowers",
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
                    "date_time",
                    models.DateTimeField(
                        help_text="Datum und Uhrzeit des Datenpunktes",
                        verbose_name="Zeitpunkt",
                    ),
                ),
                (
                    "followers",
                    models.IntegerField(
                        help_text="Anzahl der aktiven Follower",
                        verbose_name="Followers",
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
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Zuletzt upgedated"
                    ),
                ),
                (
                    "insta",
                    models.ForeignKey(
                        help_text="Globale ID des Instagram-Accounts",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="instagram_hourly_followers",
                        related_query_name="instagram_hourly_followers",
                        to="okr.insta",
                        verbose_name="Instagram-Account",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instagram Hourly Followers",
                "verbose_name_plural": "Instagram  Hourly Followers",
                "db_table": "instagram_hourly_followers",
                "ordering": ["-date_time"],
                "unique_together": {("insta", "date_time")},
            },
        ),
        migrations.CreateModel(
            name="InstaIGTV",
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
                    "external_id",
                    models.CharField(
                        max_length=25, unique=True, verbose_name="Externe ID"
                    ),
                ),
                ("created_at", models.DateTimeField(verbose_name="Erstellungsdatum")),
                (
                    "message",
                    models.TextField(
                        help_text="Beschreibungstext des IGTV Videos",
                        verbose_name="Text",
                    ),
                ),
                (
                    "video_title",
                    models.TextField(
                        help_text="Titel des IGTV Videos", verbose_name="Titel"
                    ),
                ),
                (
                    "likes",
                    models.IntegerField(
                        help_text="Anzahl der Likes", null=True, verbose_name="Likes"
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
                ("reach", models.IntegerField(null=True, verbose_name="Reichweite")),
                (
                    "impressions",
                    models.IntegerField(null=True, verbose_name="Impressions"),
                ),
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
                        verbose_name="Likes",
                    ),
                ),
                (
                    "link",
                    models.URLField(help_text="URL des Postings", verbose_name="Link"),
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
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Zuletzt upgedated"
                    ),
                ),
                (
                    "insta",
                    models.ForeignKey(
                        help_text="Globale ID des Instagram-Accounts",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="igtv_videos",
                        related_query_name="igtv_video",
                        to="okr.insta",
                        verbose_name="Instagram-Account",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instagram IGTV Video",
                "verbose_name_plural": "Instagram IGTV Videos",
                "db_table": "instagram_tv_video",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddField(
            model_name="instainsight",
            name="profile_views",
            field=models.IntegerField(null=True, verbose_name="Profilansichten"),
        ),
        migrations.AddField(
            model_name="instainsight",
            name="quintly_last_updated",
            field=models.DateTimeField(
                help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
                null=True,
                verbose_name="Zuletzt upgedated (Quintly)",
            ),
        ),
        migrations.AddField(
            model_name="instainsight",
            name="reach_28_days",
            field=models.IntegerField(
                null=True, verbose_name="Reichweite (28 Tage rollierend)"
            ),
        ),
        migrations.AddField(
            model_name="instainsight",
            name="reach_7_days",
            field=models.IntegerField(
                null=True, verbose_name="Reichweite (7 Tage rollierend)"
            ),
        ),
        migrations.AddField(
            model_name="instapost",
            name="quintly_last_updated",
            field=models.DateTimeField(
                help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
                null=True,
                verbose_name="Zuletzt upgedated (Quintly)",
            ),
        ),
        migrations.AddField(
            model_name="instapost",
            name="saved",
            field=models.IntegerField(
                help_text="Anzahl der Saves", null=True, verbose_name="Saves"
            ),
        ),
        migrations.AddField(
            model_name="instapost",
            name="video_views",
            field=models.IntegerField(
                help_text="Video-Views (3 sec oder mehr)",
                null=True,
                verbose_name="Video-Views",
            ),
        ),
        migrations.AddField(
            model_name="instastory",
            name="quintly_last_updated",
            field=models.DateTimeField(
                help_text="Zeitpunkt, zu dem Quintly die Daten zuletzt upgedated hat",
                null=True,
                verbose_name="Zuletzt upgedated (Quintly)",
            ),
        ),
        migrations.AddField(
            model_name="instastory",
            name="taps_back",
            field=models.IntegerField(
                help_text="Anzahl der back Taps", null=True, verbose_name="Taps back"
            ),
        ),
        migrations.AddField(
            model_name="instastory",
            name="taps_forward",
            field=models.IntegerField(
                help_text="Anzahl der forward Taps",
                null=True,
                verbose_name="Taps forward",
            ),
        ),
        migrations.AlterField(
            model_name="instainsight",
            name="followers",
            field=models.IntegerField(null=True, verbose_name="Follower"),
        ),
        migrations.AlterField(
            model_name="instapost",
            name="comments",
            field=models.IntegerField(
                help_text="Anzahl der Kommentare", null=True, verbose_name="Kommentare"
            ),
        ),
        migrations.AlterField(
            model_name="instapost",
            name="impressions",
            field=models.IntegerField(null=True, verbose_name="Impressions"),
        ),
        migrations.AlterField(
            model_name="instapost",
            name="likes",
            field=models.IntegerField(
                help_text="Anzahl der Likes", null=True, verbose_name="Likes"
            ),
        ),
        migrations.AlterField(
            model_name="instapost",
            name="reach",
            field=models.IntegerField(null=True, verbose_name="Reichweite"),
        ),
        migrations.AlterField(
            model_name="instastory",
            name="exits",
            field=models.IntegerField(
                help_text="Anzahl der Ausstiege", null=True, verbose_name="Exits"
            ),
        ),
        migrations.AlterField(
            model_name="instastory",
            name="impressions",
            field=models.IntegerField(null=True, verbose_name="Impressions"),
        ),
        migrations.AlterField(
            model_name="instastory",
            name="reach",
            field=models.IntegerField(null=True, verbose_name="Reichweite"),
        ),
        migrations.AlterField(
            model_name="instastory",
            name="replies",
            field=models.IntegerField(
                help_text="Anzahl der Antworten", null=True, verbose_name="Antworten"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="instainsight",
            unique_together={("insta", "date")},
        ),
        migrations.DeleteModel(
            name="InstaCollaboration",
        ),
        migrations.DeleteModel(
            name="InstaCollaborationType",
        ),
        migrations.RemoveField(
            model_name="instainsight",
            name="followers_change",
        ),
        migrations.RemoveField(
            model_name="instainsight",
            name="interval",
        ),
        migrations.RemoveField(
            model_name="instainsight",
            name="posts_change",
        ),
    ]
