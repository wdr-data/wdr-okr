# Generated by Django 3.0.7 on 2020-06-25 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Insta",
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
                ("name", models.CharField(max_length=200)),
                ("quintly_profile_id", models.IntegerField()),
            ],
            options={
                "verbose_name": "Instagram-Account",
                "verbose_name_plural": "Instagram-Accounts",
            },
        ),
        migrations.CreateModel(
            name="InstaStory",
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
                    models.CharField(max_length=25, unique=True, verbose_name="ID"),
                ),
                ("caption", models.TextField(verbose_name="Text", null=True)),
                ("time", models.DateTimeField(verbose_name="Erstellt")),
                ("story_type", models.CharField(max_length=200, verbose_name="Typ")),
                ("replies", models.IntegerField(verbose_name="Antworten")),
                ("exits", models.IntegerField(verbose_name="Exits")),
                ("reach", models.IntegerField(verbose_name="Reichweite")),
                ("impressions", models.IntegerField(verbose_name="Impressions")),
                ("link", models.URLField(max_length=1024, verbose_name="Link")),
                (
                    "insta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stories",
                        related_query_name="story",
                        to="okr.Insta",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instagram-Story",
                "verbose_name_plural": "Instagram-Stories",
            },
        ),
        migrations.CreateModel(
            name="InstaPost",
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
                    models.CharField(max_length=25, unique=True, verbose_name="ID"),
                ),
                ("message", models.TextField(verbose_name="Text")),
                ("time", models.DateTimeField(verbose_name="Erstellt")),
                ("post_type", models.CharField(max_length=20, verbose_name="Typ")),
                ("comments", models.IntegerField(verbose_name="Kommentare")),
                ("likes", models.IntegerField(verbose_name="Likes")),
                ("reach", models.IntegerField(verbose_name="Reichweite")),
                ("impressions", models.IntegerField(verbose_name="Impressions")),
                ("link", models.URLField(verbose_name="Link")),
                (
                    "insta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        related_query_name="post",
                        to="okr.Insta",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instagram-Post",
                "verbose_name_plural": "Instagram-Posts",
            },
        ),
        migrations.CreateModel(
            name="InstaCollaboration",
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
                ("time", models.DateField(verbose_name="Datum")),
                (
                    "influencer",
                    models.CharField(max_length=100, verbose_name="Influencer*in"),
                ),
                ("followers", models.IntegerField(verbose_name="Follower")),
                ("description", models.TextField(verbose_name="Beschreibung")),
                (
                    "insta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collaborations",
                        related_query_name="collaboration",
                        to="okr.Insta",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instagram-Collaboration",
                "verbose_name_plural": "Instagram-Collaborations",
            },
        ),
        migrations.CreateModel(
            name="InstaInsight",
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
                ("time", models.DateField(verbose_name="Datum")),
                (
                    "interval",
                    models.CharField(
                        choices=[
                            ("daily", "Täglich"),
                            ("weekly", "Wöchentlich"),
                            ("monthly", "Monatlich"),
                        ],
                        max_length=10,
                        verbose_name="Zeitraum",
                    ),
                ),
                ("reach", models.IntegerField(null=True, verbose_name="Reichweite")),
                (
                    "impressions",
                    models.IntegerField(null=True, verbose_name="Impressions"),
                ),
                ("followers", models.IntegerField(verbose_name="Follower")),
                (
                    "followers_change",
                    models.IntegerField(verbose_name="Veränderung Follower"),
                ),
                ("posts_change", models.IntegerField(verbose_name="Veränderung Posts")),
                (
                    "text_message_clicks_day",
                    models.IntegerField(null=True, verbose_name="Nachricht senden"),
                ),
                (
                    "email_contacts_day",
                    models.IntegerField(null=True, verbose_name="Email senden"),
                ),
                (
                    "insta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="insights",
                        related_query_name="insight",
                        to="okr.Insta",
                    ),
                ),
            ],
            options={
                "verbose_name": "Instagram-Insight",
                "verbose_name_plural": "Instagram-Insights",
                "unique_together": {("insta", "time", "interval")},
            },
        ),
    ]
