# Generated by Django 3.2.7 on 2021-10-13 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('okr', '0074_auto_20210915_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='ard_audiothek_id',
            field=models.CharField(help_text='ARD Audiothek ID, falls vorhanden', max_length=32, null=True, verbose_name='ARD Audiothek ID'),
        ),
        migrations.AddField(
            model_name='podcastepisode',
            name='ard_audiothek_id',
            field=models.CharField(help_text='ARD Audiothek ID, falls vorhanden', max_length=32, null=True, verbose_name='ARD Audiothek ID'),
        ),
        migrations.CreateModel(
            name='PodcastEpisodeDataArdAudiothekPerformance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Datum der Performance-Daten', verbose_name='Datum')),
                ('starts', models.IntegerField(help_text='Wiedergaben der Episode', verbose_name='Wiedergaben')),
                ('playback_time', models.DurationField(help_text='Abspieldauer der Episode (HH:MM:SS)', verbose_name='Spieldauer')),
                ('last_updated', models.DateTimeField(auto_now=True, help_text='Zeitpunkt der Datenaktualisierung', verbose_name='Zuletzt upgedated')),
                ('episode', models.ForeignKey(help_text='Globale ID der Episode', on_delete=django.db.models.deletion.CASCADE, related_name='data_ard_audiothek_performance', related_query_name='data_ard_audiothek_performance', to='okr.podcastepisode', verbose_name='Episode')),
            ],
            options={
                'verbose_name': 'Podcast-Episoden-Performance (ARD Audiothek)',
                'verbose_name_plural': 'Podcast-Episoden-Performance (ARD Audiothek)',
                'db_table': 'podcast_episode_data_ard_audiothek_performance',
                'ordering': ['-date', 'episode'],
                'unique_together': {('date', 'episode')},
            },
        ),
    ]
