import datetime as dt
from time import sleep
import pytz
import gc
import functools

from django.db.utils import IntegrityError
from django.db.models import Q
from bulk_sync import bulk_sync
from sentry_sdk import capture_exception
from spotipy.exceptions import SpotifyException

from . import feed
from . import spotify
from . import podstat
from .spotify_api import spotify_api, fetch_all
from ..common.utils import local_today, local_yesterday, date_range
from ...models import (
    Podcast,
    PodcastEpisode,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataPodstat,
    PodcastEpisodeDataSpotifyUser,
    PodcastDataSpotify,
)

berlin = pytz.timezone("Europe/Berlin")


def scrape_full(podcast):
    print("Running full scrape of", podcast)

    podcast_filter = Q(id=podcast.id)
    start_date = dt.date(2016, 1, 1)

    sleep(1)
    scrape_feed(podcast_filter=podcast_filter)

    sleep(1)
    scrape_spotify_mediatrend(start_date=start_date, podcast_filter=podcast_filter)

    sleep(1)
    scrape_spotify_api(start_date=start_date, podcast_filter=podcast_filter)

    sleep(1)
    scrape_podstat(start_date=start_date, podcast_filter=podcast_filter)

    print("Finished full scrape of", podcast)


def scrape_feed(*, podcast_filter=None):
    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        print("Scraping feed for", podcast)

        # Create mapping from episode title to object for faster lookups
        if podcast.spotify_id:
            licensed_episodes = spotify_api.podcast_episodes(podcast.spotify_id)

            spotify_episode_id_by_name = {}
            spotify_episode_ids_search = list(
                reversed(
                    list(
                        uri.replace("spotify:episode:", "")
                        for uri in licensed_episodes["episodes"].keys()
                    )
                )
            )
            # Search Podcaster API
            for episode_id in spotify_episode_ids_search:
                ep_meta = spotify_api.podcast_episode_meta(
                    podcast.spotify_id, episode_id
                )

                spotify_episode_id_by_name[ep_meta["name"]] = episode_id

            # Try to fill up with public API information as well, where available
            ep_metas_public = fetch_all(
                functools.partial(spotify_api.episodes, market="de"),
                spotify_episode_ids_search,
                "episodes",
            )
            for episode_id, ep_meta_public in zip(
                spotify_episode_ids_search, ep_metas_public
            ):
                if ep_meta_public:
                    spotify_episode_id_by_name[ep_meta_public["name"]] = episode_id

        else:
            spotify_episode_id_by_name = {}

        d = feed.parse(podcast.feed_url)
        for entry in d.entries:
            spotify_id = spotify_episode_id_by_name.get(entry.title)

            media_url = entry.enclosures[0].href
            zmdb_id = int(media_url.split("/")[-2])
            t = dt.datetime.strptime(entry.itunes_duration, "%H:%M:%S")
            duration = dt.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            publication_date_time = dt.datetime(
                *entry.published_parsed[:6], tzinfo=pytz.UTC
            )
            defaults = {
                "podcast": podcast,
                "title": entry.title,
                "description": entry.description,
                "publication_date_time": publication_date_time,
                "media": media_url,
                "spotify_id": spotify_id,
                "duration": duration,
            }

            try:
                obj, created = PodcastEpisode.objects.update_or_create(
                    zmdb_id=zmdb_id,
                    defaults=defaults,
                )
            except IntegrityError as e:
                capture_exception(e)
                print(
                    f"Data for {entry.title} failed integrity check:",
                    defaults,
                    sep="\n",
                )


def scrape_spotify_api(*, start_date=None, podcast_filter=None):
    today = local_today()
    yesterday = local_yesterday()

    if start_date is None:
        start_date = yesterday - dt.timedelta(days=5)

    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        print("Scraping spotify API for", podcast)

        if not podcast.spotify_id:
            print("No Spotify ID for", podcast)
            continue

        spotify_followers_objects = []
        spotify_data_objects = []
        spotify_user_objects = []

        # Scrape follower and listener data for podcast (ignores start_date)
        follower_data = spotify_api.podcast_followers(podcast.spotify_id)

        first_episode_date = podcast.episodes.order_by("publication_date_time")[
            0
        ].publication_date_time.date()

        if start_date < first_episode_date:
            start_date = first_episode_date

        for date in reversed(date_range(start_date, yesterday)):

            try:
                listener_data_all_time = spotify_api.podcast_data_all_time(
                    podcast.spotify_id, "listeners", end=date
                )
            except SpotifyException:
                print("No Podcast data anymore for", date)
                break

            try:
                listener_data = spotify_api.podcast_data(
                    podcast.spotify_id, "listeners", date
                )
            except SpotifyException:
                listener_data = {"total": 0}

            defaults = {
                "listeners_all_time": listener_data_all_time["total"],
                "listeners": listener_data["total"],
            }

            if date == yesterday:
                defaults["followers"] = follower_data["total"]

            existing = PodcastDataSpotify.objects.filter(
                podcast=podcast,
                date=date,
            )
            if existing.count() > 0:
                existing.update(**defaults)
            else:
                if "followers" not in defaults:
                    defaults["followers"] = 0

                obj = PodcastDataSpotify(podcast=podcast, date=date, **defaults)
                obj.save()

        # Episodes
        for podcast_episode in podcast.episodes.all():
            print("Scraping spotify episode data for", podcast_episode)

            if not podcast_episode.spotify_id:
                print("No Spotify ID for", podcast_episode)
                continue

            # Scrape stream stats for episode
            for date in date_range(start_date, yesterday):
                if date < podcast_episode.publication_date_time.date():
                    continue

                episode_data = {}

                for agg_type in ("starts", "streams", "listeners"):
                    try:
                        result = spotify_api.podcast_episode_data(
                            podcast.spotify_id,
                            podcast_episode.spotify_id,
                            agg_type,
                            date,
                        )
                        episode_data[agg_type] = result
                    except SpotifyException as e:
                        episode_data[agg_type] = {"total": 0}

                try:
                    episode_data[
                        "listeners_all_time"
                    ] = spotify_api.podcast_episode_data_all_time(
                        podcast.spotify_id,
                        podcast_episode.spotify_id,
                        "listeners",
                        end=date,
                    )
                except SpotifyException as e:
                    episode_data["listeners_all_time"] = {"total": 0}

                spotify_data_objects.append(
                    _scrape_episode_data_spotify(podcast_episode, date, episode_data)
                )

        if spotify_data_objects:
            result_spotify = bulk_sync(
                new_models=spotify_data_objects,
                key_fields=["date", "episode"],
                batch_size=100,
                skip_deletes=True,
                filters=None,
            )
            print("Spotify bulk objects:", result_spotify)

        gc.collect()


def scrape_spotify_mediatrend(*, start_date=None, podcast_filter=None):

    if start_date is None:
        start_date = dt.date.today() - dt.timedelta(days=20)

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

            spotify_user_objects = []

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

                # Scrape user stats for episode
                Additional = connection_meta.classes.Additional
                dates = set()
                for (
                    user_data
                ) in spotify_episode.episode_data_additional_collection.filter(
                    Additional.datum >= start_date
                ):
                    if user_data.datum in dates:
                        print("Multiple spotify user stats for", user_data.datum)
                        continue

                    spotify_user_objects.append(
                        _scrape_episode_data_spotify_user(podcast_episode, user_data)
                    )

                    dates.add(user_data.datum)

            if spotify_user_objects:
                result_spotify_user = bulk_sync(
                    new_models=spotify_user_objects,
                    key_fields=["date", "episode"],
                    batch_size=100,
                    skip_deletes=True,
                    filters=None,
                )
                print("Spotify user bulk objects:", result_spotify_user)

        del connection_meta
        gc.collect()


def _scrape_episode_data_spotify(podcast_episode, date, stream_data):

    return PodcastEpisodeDataSpotify(
        episode=podcast_episode,
        date=date,
        starts=stream_data["starts"]["total"],
        streams=stream_data["streams"]["total"],
        listeners=stream_data["listeners"]["total"],
        listeners_all_time=stream_data["listeners_all_time"]["total"],
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


def scrape_podstat(*, start_date=None, podcast_filter=None):

    if start_date is None:
        start_date = dt.date.today() - dt.timedelta(days=20)

    start_time = int(
        dt.datetime(start_date.year, start_date.month, start_date.day).timestamp()
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
                    objects_episode = _aggregate_episode_data(objects_episode)
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
                    "Podstat bulk sync results for podcast",
                    podcast,
                    result_podstat,
                )

        gc.collect()


def _scrape_episode_data_podstat_ondemand(podcast_episode, podcast_ucount):
    ucount_date = dt.datetime.fromtimestamp(podcast_ucount.zeit, berlin).date()

    return {
        "episode": podcast_episode,
        "date": ucount_date,
        "ondemand": podcast_ucount.nv,
        "downloads": 0,
    }


def _scrape_episode_data_podstat_download(podcast_episode, podcast_ucount):
    ucount_date = dt.datetime.fromtimestamp(podcast_ucount.zeit, berlin).date()

    return {
        "episode": podcast_episode,
        "date": ucount_date,
        "downloads": podcast_ucount.nv,
        "ondemand": 0,
    }


def _aggregate_episode_data(data_objects):
    cache = {}

    for obj in data_objects:
        podstat_obj = PodcastEpisodeDataPodstat(
            episode=obj["episode"],
            date=obj["date"],
            downloads=obj["downloads"],
            ondemand=obj["ondemand"],
        )
        if podstat_obj.date in cache:
            existing = cache[podstat_obj.date]
            existing.downloads += podstat_obj.downloads
            existing.ondemand += podstat_obj.ondemand
        else:
            cache[podstat_obj.date] = podstat_obj

    return list(cache.values())
