# Generated by Django 3.1.7 on 2021-03-31 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('okr', '0055_customkeyresult_customkeyresultrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='main_category',
            field=models.ForeignKey(blank=True, null=True, help_text='Die für den Podcast hier manuell vergebene Hauptkategorie', on_delete=django.db.models.deletion.RESTRICT, related_name='podcasts_main', related_query_name='podcast_main', to='okr.podcastcategory', verbose_name='Hauptkategorie'),
        ),
        migrations.AlterField(
            model_name='podcast',
            name='categories',
            field=models.ManyToManyField(blank=True, db_table='podcast_podcast_category', help_text='Die für den Podcast hier manuell vergebenen Kategorien. Die Hauptkategorie ist hier ebenfalls auszuwählen!', related_name='podcasts', related_query_name='podcast', to='okr.PodcastCategory', verbose_name='Kategorien'),
        ),
    ]
