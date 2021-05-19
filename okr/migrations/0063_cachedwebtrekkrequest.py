# Generated by Django 3.2 on 2021-05-18 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0062_auto_20210430_1631"),
    ]

    operations = [
        migrations.CreateModel(
            name="CachedWebtrekkRequest",
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
                    "payload",
                    models.TextField(
                        help_text="Query-Payload für Archiv-Eintrag",
                        unique=True,
                        verbose_name="Webtrekk Query-Payload",
                    ),
                ),
                (
                    "response",
                    models.TextField(
                        help_text="API-Response von Webtrekk",
                        verbose_name="Webtrekk Response",
                    ),
                ),
                (
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Jüngste Aktualisierung des Datenpunktes",
                        verbose_name="Zuletzt upgedated",
                    ),
                ),
            ],
            options={
                "verbose_name": "Webtrekk Cache-Eintrag",
                "verbose_name_plural": "Webtrekk Cache-Einträge",
                "db_table": "cached_webtrekk_request",
                "ordering": ["last_updated"],
            },
        ),
    ]
