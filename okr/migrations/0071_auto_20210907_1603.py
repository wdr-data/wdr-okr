# Generated by Django 3.2.5 on 2021-09-07 14:03

from time import sleep

from django.db import migrations, models


def delete_non_daily_intervals(apps, schema_editor):
    FacebookInsight = apps.get_model("okr", "FacebookInsight")
    TwitterInsight = apps.get_model("okr", "TwitterInsight")
    TikTokData = apps.get_model("okr", "TikTokData")

    interval_models = (
        FacebookInsight,
        TwitterInsight,
        TikTokData,
    )

    for Model in interval_models:
        Model.objects.exclude(interval="daily").delete()

    sleep(5)


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0070_auto_20210823_1654"),
    ]

    operations = [
        migrations.RunPython(delete_non_daily_intervals),
        migrations.AddField(
            model_name="facebookinsight",
            name="impressions_unique_28_days",
            field=models.IntegerField(
                null=True, verbose_name="Unique Impressions (28 Tage)"
            ),
        ),
        migrations.AddField(
            model_name="facebookinsight",
            name="impressions_unique_7_days",
            field=models.IntegerField(
                null=True, verbose_name="Unique Impressions (7 Tage)"
            ),
        ),
        migrations.AlterField(
            model_name="facebookinsight",
            name="impressions_unique",
            field=models.IntegerField(verbose_name="Unique Impressions"),
        ),
        migrations.AlterUniqueTogether(
            name="facebookinsight",
            unique_together={("facebook", "date")},
        ),
        migrations.AlterUniqueTogether(
            name="tiktokdata",
            unique_together={("tiktok", "date")},
        ),
        migrations.AlterUniqueTogether(
            name="twitterinsight",
            unique_together={("twitter", "date")},
        ),
        migrations.RemoveField(
            model_name="facebookinsight",
            name="interval",
        ),
        migrations.RemoveField(
            model_name="tiktokdata",
            name="interval",
        ),
        migrations.RemoveField(
            model_name="twitterinsight",
            name="interval",
        ),
    ]
