# Generated by Django 3.0.8 on 2020-07-21 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('okr', '0011_podcast_podcastdataspotifyfollowers_podcastepisode_podcastepisodedatapodstatdownload_podcastepisoded'),
    ]

    operations = [
        migrations.RenameField(
            model_name='podcastepisode',
            old_name='duratation',
            new_name='duration',
        ),
    ]
