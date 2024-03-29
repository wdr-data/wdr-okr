# Generated by Django 4.2.5 on 2024-01-25 11:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("okr", "0085_alter_tiktokdata_videos"),
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
                    ("no_link_embedded", "Kein Link (eingebettet)"),
                    ("no_link_other", "Kein Link (sonstiges)"),
                    ("notification", "Benachrichtigung"),
                    ("playlist", "Playlist"),
                    ("promoted", "Promoted"),
                    ("related_video", "Related"),
                    ("shorts", "Shorts"),
                    ("sound_page", "Soundpage"),
                    ("subscriber", "Abonnent*in"),
                    ("yt_channel", "Youtube-Kanal"),
                    ("yt_other_page", "Sonstige Youtube-Seite"),
                    ("yt_playlist_page", "Youtube Playlist-Seite"),
                    ("yt_search", "Youtube-Suche"),
                    ("hashtags", "Hashtags"),
                    ("shorts_content_links", "Shorts Content Links"),
                ],
                max_length=40,
                verbose_name="Source Type",
            ),
        ),
        migrations.AlterField(
            model_name="youtubevideotrafficsource",
            name="source_type",
            field=models.CharField(
                choices=[
                    ("0: Direct or unknown", "Direct or unknown"),
                    ("1: YouTube advertising", "YouTube advertising"),
                    ("3: Browse features", "Browse features"),
                    ("4: YouTube channels", "YouTube channels"),
                    ("5: YouTube search", "YouTube search"),
                    ("7: Suggested videos", "Suggested videos"),
                    ("8: Other YouTube features", "Other YouTube features"),
                    ("9: External", "External"),
                    ("11: Video cards and annotations", "Video cards and annotations"),
                    ("14: Playlists", "Playlists"),
                    ("17: Notifications", "Notifications"),
                    ("18: Playlist pages", "Playlist pages"),
                    (
                        "19: Programming from claimed content",
                        "Programming from claimed content",
                    ),
                    ("20: Interactive video endscreen", "Interactive video endscreen"),
                    ("23: Stories", "Stories"),
                    ("24: Shorts", "Shorts"),
                    ("25: Product Pages", "Product Pages"),
                    ("26: Hashtag Pages", "Hashtag Pages"),
                    ("27: Sound Pages", "Sound Pages"),
                    ("28: Live redirect", "Live redirect"),
                    ("30: Remixed video", "Remixed video"),
                    ("31: Vertical live feed", "Vertical live feed"),
                    ("32: Related video", "Related video"),
                ],
                max_length=40,
                verbose_name="Source Type",
            ),
        ),
    ]
