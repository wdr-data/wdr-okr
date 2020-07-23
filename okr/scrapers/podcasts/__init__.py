from datetime import date, datetime, timedelta
import pytz

from django.db.utils import IntegrityError

from . import feed
from . import spotify
from . import podstat
from ...models import (
    Podcast,
    PodcastEpisode,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataSpotifyUser,
    PodcastDataSpotifyFollowers,
    PodcastEpisodeDataPodstatOndemand,
    PodcastEpisodeDataPodstatDownload,
)

berlin = pytz.timezone("Europe/Berlin")


def scrape_feed():
    for podcast in Podcast.objects.all():
        d = feed.parse(podcast.feed_url)
        for entry in d.entries:
            media_url = entry.enclosures[0].href
            zmdb_id = int(media_url.split("/")[-2])
            t = datetime.strptime(entry.itunes_duration, "%H:%M:%S")
            duration = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            publication_date_time = datetime(
                *entry.published_parsed[:6], tzinfo=pytz.UTC
            )
            defaults = {
                "podcast": podcast,
                "title": entry.title,
                "description": entry.description,
                "publication_date_time": publication_date_time,
                "media": media_url,
                "duration": duration,
            }

            try:
                obj, created = PodcastEpisode.objects.update_or_create(
                    zmdb_id=zmdb_id, defaults=defaults,
                )
            except IntegrityError:
                print(
                    f"Data for {entry.title} failed integrity check:",
                    defaults,
                    sep="\n",
                )


def scrape_spotify(*, start_date=None):

    if start_date is None:
        start_date = date.today() - timedelta(days=31)

    with spotify.make_connection_meta() as connection_meta:
        for podcast in Podcast.objects.all():
            spotify_podcast = spotify.get_podcast(connection_meta, podcast.name)

            # Scrape follower data for podcast
            FollowersData = connection_meta.classes.FollowersData
            for followers_data in spotify_podcast.podcasts_follower_collection.filter(
                FollowersData.datum >= start_date
            ):
                _scrape_podcast_data_spotify_followers(podcast, followers_data)

            # Create mapping from episode title to object for faster lookups
            spotify_episodes = {}
            for ep in spotify_podcast.episodes_collection:
                if ep.episode in spotify_episodes:
                    print(
                        "Found multiple matches for Spotify episode",
                        podcast_episode,
                        "in external database.",
                    )

                spotify_episodes[ep.episode] = ep

            for podcast_episode in podcast.episodes.all():
                try:
                    spotify_episode = spotify_episodes[podcast_episode.title]
                except KeyError:
                    print(
                        "Could not find Spotify episode",
                        podcast_episode,
                        "in external database.",
                    )
                    continue

                # Scrape stream stats for episode
                Stream = connection_meta.classes.Stream
                for (
                    stream_data
                ) in spotify_episode.episode_data_streams_collection.filter(
                    Stream.datum >= start_date
                ):
                    _scrape_episode_data_spotify(podcast_episode, stream_data)

                # Scrape user stats for episode
                Additional = connection_meta.classes.Additional
                for (
                    user_data
                ) in spotify_episode.episode_data_additional_collection.filter(
                    Additional.datum >= start_date
                ):
                    _scrape_episode_data_spotify_user(podcast_episode, user_data)


def _scrape_episode_data_spotify(podcast_episode, stream_data):
    if stream_data.datum is None:
        print(f"Date for stream data of episode {podcast_episode} is NULL")
        return

    defaults = {
        "starts": stream_data.starts,
        "streams": stream_data.streams,
        "listeners": stream_data.listeners,
    }

    try:
        obj, created = PodcastEpisodeDataSpotify.objects.update_or_create(
            episode=podcast_episode, date=stream_data.datum, defaults=defaults,
        )
    except IntegrityError:
        print(
            f"Spotify data for episode {podcast_episode} on {stream_data.datum} failed integrity check:",
            defaults,
            sep="\n",
        )


def _scrape_episode_data_spotify_user(podcast_episode, user_data):
    if user_data.datum is None:
        print(f"Date for stream data of episode {podcast_episode} is NULL")
        return

    # Use getattr because the column name has a minus in it
    defaults = {
        "age_0_17": getattr(user_data, "age_0-17"),
        "age_18_22": getattr(user_data, "age_18-22"),
        "age_23_27": getattr(user_data, "age_23-27"),
        "age_28_34": getattr(user_data, "age_28-34"),
        "age_35_44": getattr(user_data, "age_35-44"),
        "age_45_59": getattr(user_data, "age_45-59"),
        "age_60_150": getattr(user_data, "age_60-150"),
        "age_unknown": user_data.age_unknown,
        "gender_female": user_data.gender_female,
        "gender_male": user_data.gender_male,
        "gender_non_binary": user_data.gender_non_binary,
        "gender_not_specified": user_data.gender_not_specified,
    }

    try:
        obj, created = PodcastEpisodeDataSpotifyUser.objects.update_or_create(
            episode=podcast_episode, date=user_data.datum, defaults=defaults,
        )
    except IntegrityError:
        print(
            f"Spotify user data for episode {podcast_episode} on {user_data.datum} failed integrity check:",
            defaults,
            sep="\n",
        )


def _scrape_podcast_data_spotify_followers(podcast, follower_data):
    if follower_data.datum is None:
        print(f"Date for follower data of podcast {podcast} is NULL")
        return

    defaults = {
        "followers": follower_data.followers,
    }

    try:
        obj, created = PodcastDataSpotifyFollowers.objects.update_or_create(
            podcast=podcast, date=follower_data.datum, defaults=defaults,
        )
    except IntegrityError:
        print(
            f"Spotify follower data for podcast {podcast} on {follower_data.datum} failed integrity check:",
            defaults,
            sep="\n",
        )


def scrape_podstat(*, start_date=None):

    if start_date is None:
        start_date = date.today() - timedelta(days=31)

    with podstat.make_connection_meta() as connection_meta:
        for podcast in Podcast.objects.all():
            for podcast_episode in podcast.episodes.all():
                podstat_episode_variants = podstat.get_episode(
                    connection_meta, podcast_episode.zmdb_id
                )
                if len(podstat_episode_variants) != 2:
                    print(
                        f"Expected 2 variants of episode {podcast_episode} in podstat data, found {len(podstat_episode_variants)}"
                    )

                for variant in podstat_episode_variants:
                    variant_type = variant.podcast_murl.hinweis
                    for podcast_ucount in variant.podcast_ucount_tag_collection:
                        if (
                            datetime.fromtimestamp(podcast_ucount.zeit, berlin).date()
                            < start_date
                        ):
                            continue

                        if variant_type == "O":
                            _scrape_episode_data_podstat_ondemand(
                                podcast_episode, podcast_ucount
                            )
                        elif variant_type == "D":
                            _scrape_episode_data_podstat_download(
                                podcast_episode, podcast_ucount
                            )


def _scrape_episode_data_podstat_ondemand(podcast_episode, podcast_ucount):
    ucount_date = datetime.fromtimestamp(podcast_ucount.zeit, berlin).date()

    defaults = {
        "nv": podcast_ucount.nv,
        "nv10": podcast_ucount.nv10,
    }
    try:
        obj, created = PodcastEpisodeDataPodstatOndemand.objects.update_or_create(
            episode=podcast_episode, date=ucount_date, defaults=defaults,
        )
    except IntegrityError:
        print(
            f"Podstat ondemand data for episode {podcast_episode} on {ucount_date} failed integrity check:",
            defaults,
            sep="\n",
        )


def _scrape_episode_data_podstat_download(podcast_episode, podcast_ucount):
    ucount_date = datetime.fromtimestamp(podcast_ucount.zeit, berlin).date()

    defaults = {
        "nv": podcast_ucount.nv,
        "nv10": podcast_ucount.nv10,
    }
    try:
        obj, created = PodcastEpisodeDataPodstatDownload.objects.update_or_create(
            episode=podcast_episode, date=ucount_date, defaults=defaults,
        )
    except IntegrityError:
        print(
            f"Podstat downloads data for episode {podcast_episode} on {ucount_date} failed integrity check:",
            defaults,
            sep="\n",
        )
