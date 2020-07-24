# Generated by Django 3.0.8 on 2020-07-24 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("okr", "0016_auto_20200723_2116"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="insta",
            options={
                "ordering": ["name"],
                "verbose_name": "Instagram-Account",
                "verbose_name_plural": "Instagram-Accounts",
            },
        ),
        migrations.AlterModelOptions(
            name="instacollaboration",
            options={
                "ordering": ["-date"],
                "verbose_name": "Instagram-Collaboration",
                "verbose_name_plural": "Instagram-Collaborations",
            },
        ),
        migrations.AlterModelOptions(
            name="instacollaborationtype",
            options={
                "ordering": ["name"],
                "verbose_name": "Instagram-Collaboration Format",
                "verbose_name_plural": "Instagram-Collaboration Formate",
            },
        ),
        migrations.AlterModelOptions(
            name="instainsight",
            options={
                "ordering": ["-date"],
                "verbose_name": "Instagram-Insight",
                "verbose_name_plural": "Instagram-Insights",
            },
        ),
        migrations.AlterModelOptions(
            name="instapost",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Instagram-Post",
                "verbose_name_plural": "Instagram-Posts",
            },
        ),
        migrations.AlterModelOptions(
            name="instastory",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Instagram-Story",
                "verbose_name_plural": "Instagram-Stories",
            },
        ),
        migrations.AlterModelOptions(
            name="podcast",
            options={
                "ordering": ["name"],
                "verbose_name": "Podcast",
                "verbose_name_plural": "Podcasts",
            },
        ),
        migrations.AlterModelOptions(
            name="podcastdataspotifyfollowers",
            options={
                "ordering": ["-date", "podcast"],
                "verbose_name": "Podcast-Spotify-Follower",
                "verbose_name_plural": "Podcast-Spotify-Follower",
            },
        ),
        migrations.AlterModelOptions(
            name="podcastepisode",
            options={
                "ordering": ["-publication_date_time"],
                "verbose_name": "Podcast-Episode",
                "verbose_name_plural": "Podcast-Episoden",
            },
        ),
        migrations.AlterModelOptions(
            name="podcastepisodedatapodstatdownload",
            options={
                "ordering": ["-date", "episode"],
                "verbose_name": "Podcast-Episoden-Downloads (Podstat)",
                "verbose_name_plural": "Podcast-Episoden-Downloads (Podstat)",
            },
        ),
        migrations.AlterModelOptions(
            name="podcastepisodedatapodstatondemand",
            options={
                "ordering": ["-date", "episode"],
                "verbose_name": "Podcast-Episoden-Streams (Podstat)",
                "verbose_name_plural": "Podcast-Episoden-Streams (Podstat)",
            },
        ),
        migrations.AlterModelOptions(
            name="podcastepisodedataspotify",
            options={
                "ordering": ["-date", "episode"],
                "verbose_name": "Podcast-Episoden-Abruf (Spotify)",
                "verbose_name_plural": "Podcast-Episoden-Abrufe (Spotify)",
            },
        ),
        migrations.AlterModelOptions(
            name="podcastepisodedataspotifyperformance",
            options={
                "ordering": ["-date", "episode"],
                "verbose_name": "Podcast-Episoden-Performance (Spotify)",
                "verbose_name_plural": "Podcast-Episoden-Performance (Spotify)",
            },
        ),
        migrations.AlterModelOptions(
            name="podcastepisodedataspotifyuser",
            options={
                "ordering": ["-date", "episode"],
                "verbose_name": "Podcast-Episoden-Nutzer (Spotify)",
                "verbose_name_plural": "Podcast-Episoden-Nutzer (Spotify)",
            },
        ),
        migrations.AlterModelOptions(
            name="youtube",
            options={
                "ordering": ["name"],
                "verbose_name": "YouTube-Account",
                "verbose_name_plural": "YouTube-Accounts",
            },
        ),
        migrations.AlterModelOptions(
            name="youtubeagerangeaverageviewduration",
            options={
                "ordering": ["-date"],
                "verbose_name": "YouTube Age-Range (Average View Duration)",
                "verbose_name_plural": "YouTube Age-Ranges (Average View Duration)",
            },
        ),
        migrations.AlterModelOptions(
            name="youtubeagerangeaverageviewpercentage",
            options={
                "ordering": ["-date"],
                "verbose_name": "YouTube Age-Range (Average Percentage Viewed)",
                "verbose_name_plural": "YouTube Age-Ranges (Average Percentage Viewed)",
            },
        ),
        migrations.AlterModelOptions(
            name="youtubeagerangeviewspercentage",
            options={
                "ordering": ["-date"],
                "verbose_name": "YouTube Age-Range (Views)",
                "verbose_name_plural": "YouTube Age-Ranges (Views)",
            },
        ),
        migrations.AlterModelOptions(
            name="youtubeagerangewatchtimepercentage",
            options={
                "ordering": ["-date"],
                "verbose_name": "YouTube Age-Range (Watch Time - Hours)",
                "verbose_name_plural": "YouTube Age-Ranges (Watch Time - Hours)",
            },
        ),
        migrations.AlterModelOptions(
            name="youtubeanalytics",
            options={
                "ordering": ["-date"],
                "verbose_name": "YouTube-Analytics",
                "verbose_name_plural": "YouTube-Analytics",
            },
        ),
        migrations.AlterModelOptions(
            name="youtubetrafficsource",
            options={
                "ordering": ["-date"],
                "verbose_name": "YouTube-TrafficSource",
                "verbose_name_plural": "YouTube-TrafficSources",
            },
        ),
        migrations.AlterField(
            model_name="podcastepisodedataspotifyperformance",
            name="average_listen",
            field=models.DurationField(
                help_text="HH:MM:SS", verbose_name="Hörzeit im Schnitt"
            ),
        ),
    ]
