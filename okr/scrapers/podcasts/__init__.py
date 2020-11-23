"""Read and process data for podcasts and podcast episodes from various data sources.
"""

import datetime as dt
from time import sleep
from typing import Optional
import gc
import functools

from django.db.utils import IntegrityError
from django.db.models import Q
from sentry_sdk import capture_exception
from spotipy.exceptions import SpotifyException

from . import feed
from . import spotify
from . import podstat
from .spotify_api import spotify_api, fetch_all
from .webtrekk import cleaned_webtrekk_audio_data
from ..common.utils import local_today, local_yesterday, date_range, BERLIN, UTC
from ...models import (
    Podcast,
    PodcastEpisode,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataPodstat,
    PodcastEpisodeDataSpotifyUser,
    PodcastDataSpotify,
    PodcastDataSpotifyHourly,
    PodcastEpisodeDataSpotifyPerformance,
    PodcastEpisodeDataWebtrekkPerformance,
)


def scrape_full(
    podcast: Podcast,
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
):
    """Read and process all available data for podcast.

    Args:
        podcast (Podcast): Podcast to scrape data for
        start_date (dt.date, optional): earliest date to request data for. Defaults to
          None.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None.
    """
    print("Running full scrape of", podcast)

    podcast_filter = Q(id=podcast.id)
    start_date = start_date or dt.date(2016, 1, 1)

    sleep(1)
    scrape_feed(podcast_filter=podcast_filter)

    sleep(1)
    scrape_spotify_mediatrend(
        start_date=start_date,
        end_date=end_date,
        podcast_filter=podcast_filter,
    )

    sleep(1)
    scrape_spotify_api(
        start_date=start_date,
        end_date=end_date,
        podcast_filter=podcast_filter,
    )

    sleep(1)
    scrape_podstat(
        start_date=start_date,
        end_date=end_date,
        podcast_filter=podcast_filter,
    )

    sleep(1)
    scrape_episode_data_webtrekk_performance(
        start_date=start_date,
        end_date=end_date,
        podcast_filter=podcast_filter,
    )

    print("Finished full scrape of", podcast)


def scrape_feed(*, podcast_filter: Optional[Q] = None):
    """Read and process data from podcast RSS feed.

    This method supplies publicly available metadata for podcast episodes. This includes
    information such as episode title, episode description, episode duration and
    ZMDB ID for the episode's media file. Additionally, this method uses the Spotify
    public API and Spotify podcaster API to determine each episode's Spotify ID, if
    one exists.

    Requesting Spotify data from both the public API and the podcaster API is necessary
    because episode names in the podaster API can be outdated. On the other hand, only
    the podcaster API contains information about de-published episodes. Data from both
    APIs is required to make mapping by episode name possible.

    Args:
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        print("Scraping feed for", podcast)

        # For podcasts that are available on Spotify: Map episode title to Spotify ID
        # for faster lookups
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

            # Try to read additional, publicly available data from Spotify's public API
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
        # Leave Spotify ID empty of no matching ID was found
        else:
            spotify_episode_id_by_name = {}

        # Read data from RSS feed
        d = feed.parse(podcast.feed_url)
        for entry in d.entries:
            spotify_id = spotify_episode_id_by_name.get(entry.title)

            media_url = entry.enclosures[0].href
            zmdb_id = int(media_url.split("/")[-2])
            t = dt.datetime.strptime(entry.itunes_duration, "%H:%M:%S")
            duration = dt.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            publication_date_time = dt.datetime(*entry.published_parsed[:6], tzinfo=UTC)
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


def scrape_spotify_api(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Read and process data from Spotify API.

    This method supplies two kinds of Spotify-related data:

    a) Data about the podcast itself, such as the current number of the podcast's
    followers

    b) Client side usage data for each podcast episode. This includes starts, streams
    (minimum listening duration of 1 minute), or listeners (number of accounts).

    Args:
        start_date (dt.date, optional): Earliest date to request data for. Defaults to
          None.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None.
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    yesterday = local_yesterday()

    if start_date is None:
        start_date = yesterday - dt.timedelta(days=5)

    end_date = end_date or yesterday

    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        print("Scraping spotify API for", podcast)

        if not podcast.spotify_id:
            print("No Spotify ID for", podcast)
            continue

        # Retrieve follower and listener data for podcast
        follower_data = spotify_api.podcast_followers(podcast.spotify_id)

        first_episode_date = podcast.episodes.order_by("publication_date_time")[
            0
        ].publication_date_time.date()

        if start_date < first_episode_date:
            start_date = first_episode_date

        for date in reversed(date_range(start_date, end_date)):
            # Read daily data
            try:
                listener_data_all_time = spotify_api.podcast_data_date_range(
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

            try:
                listener_weekly_data = spotify_api.podcast_data_date_range(
                    podcast.spotify_id,
                    "listeners",
                    start=date - dt.timedelta(days=7),
                    end=date,
                )
            except SpotifyException:
                listener_weekly_data = {"total": 0}

            try:
                listener_monthly_data = spotify_api.podcast_data_date_range(
                    podcast.spotify_id,
                    "listeners",
                    start=date - dt.timedelta(days=30),
                    end=date,
                )
            except SpotifyException:
                listener_monthly_data = {"total": 0}

            defaults = {
                "listeners_all_time": listener_data_all_time["total"],
                "listeners": listener_data["total"],
                "listeners_weekly": listener_weekly_data["total"],
                "listeners_monthly": listener_monthly_data["total"],
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

            # Read hourly data
            if date < dt.date(2019, 12, 1):
                continue

            for hour in range(0, 24):
                agg_type_data = {}
                date_time = dt.datetime(
                    date.year, date.month, date.day, hour, tzinfo=UTC
                )
                for agg_type in ["starts", "streams"]:
                    try:
                        agg_type_data[agg_type] = spotify_api.podcast_data(
                            podcast.spotify_id,
                            agg_type,
                            date_time,
                            precision=spotify_api.Precision.HOUR,
                        )["total"]
                    except:
                        agg_type_data[agg_type] = 0

                PodcastDataSpotifyHourly.objects.update_or_create(
                    podcast=podcast,
                    date_time=date_time,
                    defaults=agg_type_data,
                )

        # Retrieve data for individual episodes
        for podcast_episode in podcast.episodes.all():
            print("Scraping spotify episode data for", podcast_episode)

            if not podcast_episode.spotify_id:
                print("No Spotify ID for", podcast_episode)
                continue

            # Scrape stream stats for episode
            for date in date_range(start_date, end_date):
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

                PodcastEpisodeDataSpotify.objects.update_or_create(
                    episode=podcast_episode,
                    date=date,
                    defaults=dict(
                        starts=episode_data["starts"]["total"],
                        streams=episode_data["streams"]["total"],
                        listeners=episode_data["listeners"]["total"],
                        listeners_all_time=episode_data["listeners_all_time"]["total"],
                    ),
                )

        gc.collect()


def scrape_spotify_mediatrend(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Read and process data from Spotify Mediatrend.

    This method supplies demographical data and other items that are only available
    through Mediatrend (and not through the Spotify API).

    Args:
        start_date (dt.date, optional): Earliest date to request data for. Defaults to
          None.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None.
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    if start_date is None:
        start_date = dt.date.today() - dt.timedelta(days=20)

    end_date = end_date or local_today()

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

            # Create mapping from episode title to Spotify dataset for faster lookups
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
                    # Don't log to Sentry as the database lags behind a week
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
                    additional_data
                ) in spotify_episode.episode_data_additional_collection.filter(
                    Additional.datum >= start_date,
                    Additional.datum <= end_date,
                ):
                    if additional_data.datum in dates:
                        print("Multiple spotify user stats for", additional_data.datum)
                        continue

                    if additional_data.datum is None:
                        print(
                            f"Date for stream data of episode {podcast_episode} is NULL"
                        )
                        continue

                    PodcastEpisodeDataSpotifyUser.objects.update_or_create(
                        episode=podcast_episode,
                        date=additional_data.datum,
                        # Use getattr because the column name has a minus in it
                        defaults=dict(
                            age_0_17=getattr(additional_data, "age_0-17"),
                            age_18_22=getattr(additional_data, "age_18-22"),
                            age_23_27=getattr(additional_data, "age_23-27"),
                            age_28_34=getattr(additional_data, "age_28-34"),
                            age_35_44=getattr(additional_data, "age_35-44"),
                            age_45_59=getattr(additional_data, "age_45-59"),
                            age_60_150=getattr(additional_data, "age_60-150"),
                            age_unknown=additional_data.age_unknown,
                            gender_female=additional_data.gender_female,
                            gender_male=additional_data.gender_male,
                            gender_non_binary=additional_data.gender_non_binary,
                            gender_not_specified=additional_data.gender_not_specified,
                        ),
                    )

                    time = additional_data.average_listen
                    average_listen = dt.timedelta(
                        hours=time.hour,
                        minutes=time.minute,
                        seconds=time.second,
                    )

                    PodcastEpisodeDataSpotifyPerformance.objects.update_or_create(
                        episode=podcast_episode,
                        date=additional_data.datum,
                        # average_listen ist time --> durationfield
                        defaults=dict(
                            average_listen=average_listen,
                            quartile_1=additional_data.first_quartile,
                            quartile_2=additional_data.second_quartile,
                            quartile_3=additional_data.third_quartile,
                            complete=additional_data.complete,
                        ),
                    )

                    dates.add(additional_data.datum)

        del connection_meta
        gc.collect()


def _scrape_episode_data_spotify_performance(podcast_episode, additional_data):
    if additional_data.datum is None:
        print(f"Date for performacne data of episode {podcast_episode} is NULL")
        return

    time = getattr(additional_data, "average_listen")
    average_listen = dt.timedelta(
        hours=time.hour,
        minutes=time.minute,
        seconds=time.second,
    )

    return PodcastEpisodeDataSpotifyPerformance(
        # Use getattr because the column name has a minus in it
        episode=podcast_episode,
        date=additional_data.datum,
        # average_listen ist time --> durationfield
        average_listen=average_listen,
        quartile_1=getattr(additional_data, "first_quartile"),
        quartile_2=getattr(additional_data, "second_quartile"),
        quartile_3=getattr(additional_data, "third_quartile"),
        complete=getattr(additional_data, "complete"),
    )


def scrape_podstat(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Read and process data from Podstat.

    This method supplies data per episode of self hosted podcasts. Specifically, the
    number of download and on-demand client requests per media file for each episode.

    Args:
        start_date (dt.date, optional): Earliest date to request data for. Defaults to
          None.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None.
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    if start_date is None:
        start_date = dt.date.today() - dt.timedelta(days=20)

    end_date = end_date or local_today()

    start_time = int(
        dt.datetime(
            start_date.year,
            start_date.month,
            start_date.day,
        ).timestamp()
    )

    end_time = int(
        dt.datetime(
            end_date.year,
            end_date.month,
            end_date.day,
        ).timestamp()
    )

    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        with podstat.make_connection_meta() as connection_meta:
            print("Scraping podstat for", podcast)

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
                        PodcastCount.zeit >= start_time,
                        PodcastCount.zeit <= end_time,
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
                    for obj in objects_episode:
                        PodcastEpisodeDataPodstat.objects.update_or_create(
                            episode=obj["episode"],
                            date=obj["date"],
                            defaults=dict(
                                downloads=obj["downloads"],
                                ondemand=obj["ondemand"],
                            ),
                        )

        del connection_meta
        gc.collect()


def _scrape_episode_data_podstat_ondemand(podcast_episode, podcast_ucount):
    ucount_date = dt.datetime.fromtimestamp(podcast_ucount.zeit, BERLIN).date()

    return {
        "episode": podcast_episode,
        "date": ucount_date,
        "ondemand": podcast_ucount.nv,
        "downloads": 0,
    }


def _scrape_episode_data_podstat_download(podcast_episode, podcast_ucount):
    ucount_date = dt.datetime.fromtimestamp(podcast_ucount.zeit, BERLIN).date()

    return {
        "episode": podcast_episode,
        "date": ucount_date,
        "downloads": podcast_ucount.nv,
        "ondemand": 0,
    }


def _aggregate_episode_data(data_objects):
    cache = {}

    for obj in data_objects:
        podstat_obj = dict(
            episode=obj["episode"],
            date=obj["date"],
            downloads=obj["downloads"],
            ondemand=obj["ondemand"],
        )
        if podstat_obj["date"] in cache:
            existing = cache[podstat_obj["date"]]
            existing["downloads"] += podstat_obj["downloads"]
            existing["ondemand"] += podstat_obj["ondemand"]
        else:
            cache[podstat_obj["date"]] = podstat_obj

    return list(cache.values())


def scrape_episode_data_webtrekk_performance(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Read and process data from Webtrekk.

    This method supplies episode data from the Webtrekk database based on each episode's
    ZMDB ID.

    Args:
        start_date (dt.date, optional): Earliest date to request data for. Defaults to
          None.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None.
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    today = local_today()
    yesterday = local_yesterday()

    if start_date is None:
        start_date = yesterday - dt.timedelta(days=2)
    start_date = max(start_date, today - dt.timedelta(days=7))

    end_date = end_date or yesterday
    start_date = min(start_date, end_date)

    for date in reversed(date_range(start_date, end_date)):
        data = cleaned_webtrekk_audio_data(date)

        podcasts = Podcast.objects.all()

        if podcast_filter:
            podcasts = podcasts.filter(podcast_filter)

        for podcast in podcasts:
            for episode in podcast.episodes.all():

                if episode.zmdb_id not in data:
                    continue

                PodcastEpisodeDataWebtrekkPerformance.objects.update_or_create(
                    date=date, episode=episode, defaults=data[episode.zmdb_id]
                )
        print(f"Finished scraping of Webtrekk performance data for {date}.")
