# Generated by Django 3.0.8 on 2020-07-22 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0013_auto_20200722_1210"),
    ]

    operations = [
        migrations.AlterField(
            model_name="podcastepisodedataspotifyperformance",
            name="average_listen",
            field=models.DurationField(verbose_name="Hörzeit im Schnitt"),
        ),
    ]
