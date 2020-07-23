# Generated by Django 3.0.7 on 2020-06-25 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0004_auto_20200625_1717"),
    ]

    operations = [
        migrations.AddField(
            model_name="instacollaboration",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="instainsight",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="instapost",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="instastory",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
        migrations.AddField(
            model_name="youtubeanalytics",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, verbose_name="Zuletzt upgedated"),
        ),
    ]