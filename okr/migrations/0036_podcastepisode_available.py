# Generated by Django 3.1.4 on 2020-12-09 10:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0035_auto_20201208_1636"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcastepisode",
            name="available",
            field=models.BooleanField(
                default=True,
                help_text="Indikator, ob diese Episode momentan im Feed verfügbar ist",
                verbose_name="Verfügbar",
            ),
            preserve_default=False,
        ),
    ]
