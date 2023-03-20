# Generated by Django 3.2.5 on 2021-08-23 14:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0069_instaigtvdata"),
    ]

    operations = [
        migrations.RenameField(
            model_name="podcastdataspotify",
            old_name="listeners_weekly",
            new_name="listeners_7_days",
        ),
        migrations.RenameField(
            model_name="podcastdataspotify",
            old_name="listeners_monthly",
            new_name="listeners_28_days",
        ),
        migrations.AlterField(
            model_name="podcastdataspotify",
            name="listeners_28_days",
            field=models.IntegerField(verbose_name="Listeners (28 Tage rollierend)"),
        ),
        migrations.AlterField(
            model_name="podcastdataspotify",
            name="listeners_7_days",
            field=models.IntegerField(verbose_name="Listeners (7 Tage rollierend)"),
        ),
    ]
