# Generated by Django 5.0.7 on 2024-12-10 12:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0087_alter_youtubetrafficsource_source_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="youtubetrafficsource",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("advertising", "Werbung"),
                    ("annotation", "Annotation"),
                    ("campaign_card", "Kampagnenkarte"),
                    ("end_screen", "Endscreen"),
                    ("ext_url", "Externe URL"),
                    ("hashtags", "Hashtags"),
                    ("live_redirect", "Live-Weiterleitung"),
                    ("no_link_embedded", "Kein Link (eingebettet)"),
                    ("no_link_other", "Kein Link (sonstiges)"),
                    ("notification", "Benachrichtigung"),
                    ("playlist", "Playlist"),
                    ("product_page", "Produktseite"),
                    ("promoted", "Promoted"),
                    ("related_video", "Related"),
                    ("shorts", "Shorts"),
                    ("sound_page", "Soundpage"),
                    ("subscriber", "Abonnent*in"),
                    ("yt_channel", "Youtube-Kanal"),
                    ("yt_other_page", "Sonstige Youtube-Seite"),
                    ("yt_search", "Youtube-Suche"),
                    ("video_remixes", "Video-Remixes"),
                    ("yt_playlist_page", "Youtube Playlist-Seite"),
                    ("shorts_content_links", "Shorts Content Links"),
                    ("immersive_live", "Immersive Live"),
                ],
                max_length=40,
                verbose_name="Source Type",
            ),
        ),
    ]