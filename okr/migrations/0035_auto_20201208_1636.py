# Generated by Django 3.1.4 on 2020-12-08 15:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0034_podcastepisodedataspotifydemographics"),
    ]

    operations = [
        migrations.AlterField(
            model_name="podcastepisodedataspotifydemographics",
            name="age_range",
            field=models.CharField(
                choices=[
                    ("0-17", "0-17"),
                    ("18-22", "18-22"),
                    ("23-27", "23-27"),
                    ("28-34", "28-34"),
                    ("35-44", "35-44"),
                    ("45-59", "45-59"),
                    ("60-150", "60-150"),
                    ("unknown", "Unbekannt"),
                ],
                help_text="Die Altersgruppe, für die dieser Datenpunkt gilt.",
                max_length=20,
                verbose_name="Altersgruppe",
            ),
        ),
        migrations.AlterModelTable(
            name="podcastepisodedataspotifydemographics",
            table="podcast_episode_data_spotify_demographics",
        ),
    ]
