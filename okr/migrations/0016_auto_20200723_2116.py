# Generated by Django 3.0.8 on 2020-07-23 19:16

from django.db import migrations, models
import django.db.models.deletion


def migrate_age_ranges(apps, schema_editor):
    # Old models - YouTubeViewerAge aggregates the data and relates it to YouTube
    YouTubeViewerAge = apps.get_model("okr", "YouTubeViewerAge")

    # New models - everything relates to YouTube
    YouTubeAgeRangeAverageViewDuration = apps.get_model(
        "okr", "YouTubeAgeRangeAverageViewDuration"
    )
    YouTubeAgeRangeAverageViewPercentage = apps.get_model(
        "okr", "YouTubeAgeRangeAverageViewPercentage"
    )
    YouTubeAgeRangeViewsPercentage = apps.get_model(
        "okr", "YouTubeAgeRangeViewsPercentage"
    )
    YouTubeAgeRangeWatchTimePercentage = apps.get_model(
        "okr", "YouTubeAgeRangeWatchTimePercentage"
    )

    mapping = {
        "average_view_duration": YouTubeAgeRangeAverageViewDuration,
        "average_percentage_viewed": YouTubeAgeRangeAverageViewPercentage,
        "watch_time": YouTubeAgeRangeWatchTimePercentage,
        "views": YouTubeAgeRangeViewsPercentage,
    }

    for viewer_age in YouTubeViewerAge.objects.all():
        for viewer_age_range_attr_name, mapped_class in mapping.items():
            viewer_age_range = getattr(viewer_age, viewer_age_range_attr_name)
            obj = mapped_class(
                youtube=viewer_age.youtube,
                interval=viewer_age.interval,
                date=viewer_age.date,
                age_13_17=viewer_age_range.age_13_17,
                age_18_24=viewer_age_range.age_18_24,
                age_25_34=viewer_age_range.age_25_34,
                age_35_44=viewer_age_range.age_35_44,
                age_45_54=viewer_age_range.age_45_54,
                age_55_64=viewer_age_range.age_55_64,
                age_65_plus=viewer_age_range.age_65_plus,
            )
            obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0015_auto_20200722_1822"),
    ]

    operations = [
        migrations.CreateModel(
            name="YouTubeAgeRangeAverageViewDuration",
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
                (
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Zuletzt upgedated"
                    ),
                ),
                ("age_13_17", models.DurationField(verbose_name="13 - 17")),
                ("age_18_24", models.DurationField(verbose_name="18 - 24")),
                ("age_25_34", models.DurationField(verbose_name="25 - 34")),
                ("age_35_44", models.DurationField(verbose_name="35 - 44")),
                ("age_45_54", models.DurationField(verbose_name="45 - 54")),
                ("age_55_64", models.DurationField(verbose_name="55 - 64")),
                ("age_65_plus", models.DurationField(verbose_name="65+")),
                (
                    "youtube",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        related_query_name="+",
                        to="okr.YouTube",
                        verbose_name="YouTube-Account",
                    ),
                ),
            ],
            options={
                "verbose_name": "YouTube Age-Range (Average View Duration)",
                "verbose_name_plural": "YouTube Age-Ranges (Average View Duration)",
                "unique_together": {("youtube", "date", "interval")},
            },
        ),
        migrations.CreateModel(
            name="YouTubeAgeRangeAverageViewPercentage",
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
                (
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Zuletzt upgedated"
                    ),
                ),
                (
                    "age_13_17",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="13 - 17"
                    ),
                ),
                (
                    "age_18_24",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="18 - 24"
                    ),
                ),
                (
                    "age_25_34",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="25 - 34"
                    ),
                ),
                (
                    "age_35_44",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="35 - 44"
                    ),
                ),
                (
                    "age_45_54",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="45 - 54"
                    ),
                ),
                (
                    "age_55_64",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="55 - 64"
                    ),
                ),
                (
                    "age_65_plus",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="65+"
                    ),
                ),
                (
                    "youtube",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        related_query_name="+",
                        to="okr.YouTube",
                        verbose_name="YouTube-Account",
                    ),
                ),
            ],
            options={
                "verbose_name": "YouTube Age-Range (Average Percentage Viewed)",
                "verbose_name_plural": "YouTube Age-Ranges (Average Percentage Viewed)",
                "unique_together": {("youtube", "date", "interval")},
            },
        ),
        migrations.CreateModel(
            name="YouTubeAgeRangeViewsPercentage",
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
                (
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Zuletzt upgedated"
                    ),
                ),
                (
                    "age_13_17",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="13 - 17"
                    ),
                ),
                (
                    "age_18_24",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="18 - 24"
                    ),
                ),
                (
                    "age_25_34",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="25 - 34"
                    ),
                ),
                (
                    "age_35_44",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="35 - 44"
                    ),
                ),
                (
                    "age_45_54",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="45 - 54"
                    ),
                ),
                (
                    "age_55_64",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="55 - 64"
                    ),
                ),
                (
                    "age_65_plus",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="65+"
                    ),
                ),
                (
                    "youtube",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        related_query_name="+",
                        to="okr.YouTube",
                        verbose_name="YouTube-Account",
                    ),
                ),
            ],
            options={
                "verbose_name": "YouTube Age-Range (Views)",
                "verbose_name_plural": "YouTube Age-Ranges (Views)",
                "unique_together": {("youtube", "date", "interval")},
            },
        ),
        migrations.CreateModel(
            name="YouTubeAgeRangeWatchTimePercentage",
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
                (
                    "last_updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Zuletzt upgedated"
                    ),
                ),
                (
                    "age_13_17",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="13 - 17"
                    ),
                ),
                (
                    "age_18_24",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="18 - 24"
                    ),
                ),
                (
                    "age_25_34",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="25 - 34"
                    ),
                ),
                (
                    "age_35_44",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="35 - 44"
                    ),
                ),
                (
                    "age_45_54",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="45 - 54"
                    ),
                ),
                (
                    "age_55_64",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="55 - 64"
                    ),
                ),
                (
                    "age_65_plus",
                    models.DecimalField(
                        decimal_places=2, max_digits=5, verbose_name="65+"
                    ),
                ),
                (
                    "youtube",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        related_query_name="+",
                        to="okr.YouTube",
                        verbose_name="YouTube-Account",
                    ),
                ),
            ],
            options={
                "verbose_name": "YouTube Age-Range (Watch Time - Hours)",
                "verbose_name_plural": "YouTube Age-Ranges (Watch Time - Hours)",
                "unique_together": {("youtube", "date", "interval")},
            },
        ),
        migrations.RunPython(migrate_age_ranges),
        migrations.DeleteModel(
            name="YouTubeAgeRangeDuration",
        ),
        migrations.DeleteModel(
            name="YouTubeAgeRangePercentage",
        ),
        migrations.DeleteModel(
            name="YouTubeViewerAge",
        ),
    ]
