from datetime import date, datetime, timedelta
from time import sleep
import pytz
import gc

from django.db.utils import IntegrityError
from django.db.models import Q
from bulk_sync import bulk_sync
from sentry_sdk import capture_exception

from . import feed
from . import spotify
from . import podstat
from ...models import (
    Podcast,
    PodcastEpisode,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataPodstat,
    PodcastEpisodeDataSpotifyUser,
    PodcastDataSpotifyFollowers,
)

berlin = pytz.timezone("Europe/Berlin")


def scrape_full(podcast):
    print("Running full scrape of", podcast)

    podcast_filter = Q(id=podcast.id)
    start_date = date(2000, 1, 1)

    sleep(1)
    scrape_feed(podcast_filter=podcast_filter)

    sleep(1)
    scrape_spotify(start_date=start_date, podcast_filter=podcast_filter)

    sleep(1)
    scrape_podstat(start_date=start_date, podcast_filter=podcast_filter)

    print("Finished full scrape of", podcast)


def scrape_feed(*, podcast_filter=None):
    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        print("Scraping feed for", podcast)

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
            except IntegrityError as e:
                capture_exception(e)
                print(
                    f"Data for {entry.title} failed integrity check:",
                    defaults,
                    sep="\n",
                )


def scrape_spotify(*, start_date=None, podcast_filter=None):

    if start_date is None:
        start_date = date.today() - timedelta(days=20)

    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        with spotify.make_connection_meta() as connection_meta:
            print("Scraping spotify for", podcast)
            try:
                spotify_podcast = spotify.get_podcast(connection_meta, podcast.name)
            except IndexError as e:
                capture_exception(e)
                print("No Spotify data for", podcast)
                continue

            spotify_followers_objects = []
            spotify_objects = []
            spotify_user_objects = []

            # Scrape follower data for podcast
            FollowersData = connection_meta.classes.FollowersData
            for followers_data in spotify_podcast.podcasts_follower_collection.filter(
                FollowersData.datum >= start_date
            ):
                spotify_followers_objects.append(
                    _scrape_podcast_data_spotify_followers(podcast, followers_data)
                )

            if spotify_followers_objects:
                print("Scraping spotify followers for", podcast)
                result_spotify_followers = bulk_sync(
                    new_models=spotify_followers_objects,
                    key_fields=["date", "podcast"],
                    batch_size=100,
                    skip_deletes=True,
                    filters=None,
                )
                print("Spotify followers bulk objects:", result_spotify_followers)

            # Create mapping from episode title to object for faster lookups
            spotify_episodes = {}
            for ep in spotify_podcast.episodes_collection:
                if ep.episode in spotify_episodes:
                    print(
                        "Found multiple matches for Spotify episode",
                        ep.episode,
                        "in external database.",
                    )

                spotify_episodes[ep.episode] = ep

            for podcast_episode in podcast.episodes.all():
                print("Scraping spotify episode data for", podcast_episode)

                try:
                    spotify_episode = spotify_episodes[podcast_episode.title]
                except KeyError:
                    # Not log to Sentry as the database lags behind a week
                    print(
                        "Could not find Spotify episode",
                        podcast_episode,
                        "in external database.",
                    )
                    continue

                # Scrape stream stats for episode
                Stream = connection_meta.classes.Stream
                dates = set()
                for (
                    stream_data
                ) in spotify_episode.episode_data_streams_collection.filter(
                    Stream.datum >= start_date
                ):
                    if stream_data.datum in dates:
                        print("Multiple spotify stream stats for", stream_data.datum)
                        continue

                    spotify_objects.append(
                        _scrape_episode_data_spotify(podcast_episode, stream_data)
                    )

                    dates.add(stream_data.datum)

                # Scrape user stats for episode
                Additional = connection_meta.classes.Additional
                dates = set()
                for (
                    user_data
                ) in spotify_episode.episode_data_additional_collection.filter(
                    Additional.datum >= start_date
                ):
                    if stream_data.datum in dates:
                        print("Multiple spotify user stats for", stream_data.datum)
                        continue

                    spotify_user_objects.append(
                        _scrape_episode_data_spotify_user(podcast_episode, user_data)
                    )

                    dates.add(stream_data.datum)

            if spotify_objects:
                result_spotify = bulk_sync(
                    new_models=spotify_objects,
                    key_fields=["date", "episode"],
                    batch_size=100,
                    skip_deletes=True,
                    filters=None,
                )
                print("Spotify bulk objects:", result_spotify)

            if spotify_user_objects:
                result_spotify_user = bulk_sync(
                    new_models=spotify_user_objects,
                    key_fields=["date", "episode"],
                    batch_size=100,
                    skip_deletes=True,
                    filters=None,
                )
                print("Spotify user bulk objects:", result_spotify_user)

        gc.collect()


def _scrape_episode_data_spotify(podcast_episode, stream_data):
    if stream_data.datum is None:
        print(f"Date for stream data of episode {podcast_episode} is NULL")
        return

    return PodcastEpisodeDataSpotify(
        episode=podcast_episode,
        date=stream_data.datum,
        starts=stream_data.starts,
        streams=stream_data.streams,
        listeners=stream_data.listeners,
    )


def _scrape_episode_data_spotify_user(podcast_episode, user_data):
    if user_data.datum is None:
        print(f"Date for stream data of episode {podcast_episode} is NULL")
        return

    return PodcastEpisodeDataSpotifyUser(
        # Use getattr because the column name has a minus in it
        episode=podcast_episode,
        date=user_data.datum,
        age_0_17=getattr(user_data, "age_0-17"),
        age_18_22=getattr(user_data, "age_18-22"),
        age_23_27=getattr(user_data, "age_23-27"),
        age_28_34=getattr(user_data, "age_28-34"),
        age_35_44=getattr(user_data, "age_35-44"),
        age_45_59=getattr(user_data, "age_45-59"),
        age_60_150=getattr(user_data, "age_60-150"),
        age_unknown=user_data.age_unknown,
        gender_female=user_data.gender_female,
        gender_male=user_data.gender_male,
        gender_non_binary=user_data.gender_non_binary,
        gender_not_specified=user_data.gender_not_specified,
    )


def _scrape_podcast_data_spotify_followers(podcast, follower_data):
    if follower_data.datum is None:
        print(f"Date for follower data of podcast {podcast} is NULL")
        return

    return PodcastDataSpotifyFollowers(
        podcast=podcast, date=follower_data.datum, followers=follower_data.followers
    )


def scrape_podstat(*, start_date=None, podcast_filter=None):

    if start_date is None:
        start_date = date.today() - timedelta(days=20)

    start_time = int(
        datetime(start_date.year, start_date.month, start_date.day).timestamp()
    )

    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        with podstat.make_connection_meta() as connection_meta:
            print("Scraping podstat for", podcast)

            podstat_objects = []

            for podcast_episode in podcast.episodes.all():
                print("Scraping podstat episode data for", podcast_episode)
                podstat_episode_variants = podstat.get_episode(
                    connection_meta, podcast_episode.zmdb_id
                )
                if len(podstat_episode_variants) != 2:
                    print(
                        f"Expected 2 variants of episode {podcast_episode} in podstat data, found {len(podstat_episode_variants)}"
                    )
                ondemand_objects_episode = []
                download_objects_episode = []

                for variant in podstat_episode_variants:
                    if variant.podcast_murl is None:
                        print(
                            "No murl found for podcast_url",
                            variant.urlid,
                            "with url",
                            variant.url,
                        )
                        continue
                    else:
                        variant_type = variant.podcast_murl.hinweis

                    PodcastCount = connection_meta.classes.PodcastCount
                    for podcast_ucount in variant.podcast_ucount_tag_collection.filter(
                        PodcastCount.zeit >= start_time
                    ):
                        if variant_type == "O":
                            ondemand_objects_episode.append(
                                _scrape_episode_data_podstat_ondemand(
                                    podcast_episode, podcast_ucount
                                )
                            )
                        elif variant_type == "D":
                            download_objects_episode.append(
                                _scrape_episode_data_podstat_download(
                                    podcast_episode, podcast_ucount
                                )
                            )

                objects_episode = ondemand_objects_episode + download_objects_episode
                # Deduplicate records in case of renaming etc.
                if objects_episode:
                    objects_episode = _aggregate_episode_data(
                        objects_episode
                    )
                    print(
                        "Found",
                        len(ondemand_objects_episode),
                        "unique ondemand datapoints",
                    )
                    podstat_objects.extend(objects_episode)

            if podstat_objects:
                result_podstat = bulk_sync(
                    new_models=podstat_objects,
                    key_fields=["date", "episode"],
                    skip_deletes=True,
                    filters=None,
                )
                print(
                    "Podstat bulk sync results for podcast", podcast, result_podstat,
                )

        gc.collect()


def _scrape_episode_data_podstat_ondemand(podcast_episode, podcast_ucount):
    ucount_date = datetime.fromtimestamp(podcast_ucount.zeit, berlin).date()

    return {
        'episode': podcast_episode,
        'date': ucount_date,
        'ondemand': podcast_ucount.nv,
        'downloads': 0,
    }


def _scrape_episode_data_podstat_download(podcast_episode, podcast_ucount):
    ucount_date = datetime.fromtimestamp(podcast_ucount.zeit, berlin).date()

    return {
        'episode': podcast_episode,
        'date': ucount_date,
        'downloads': podcast_ucount.nv,
        'ondemand': 0,
    }


def _aggregate_episode_data(data_objects):
    cache = {}

    for obj in data_objects:
        podstat_obj = PodcastEpisodeDataPodstat(
            episode = obj['episode'],
            date = obj['date'],
            downloads = obj['downloads'],
            ondemand = obj['ondemand']
        )
        if podstat_obj.date in cache:
            existing = cache[podstat_obj.date]
            existing.downloads += podstat_obj.downloads
            existing.ondemand += podstat_obj.ondemand
        else:
            cache[podstat_obj.date] = podstat_obj

    return list(cache.values())
