"""Read and process data for podcasts and podcast episodes from various data sources.
"""

import datetime as dt
from time import sleep
from typing import Dict, List, Optional
import gc
import functools

from django.db.utils import IntegrityError
from django.db.models import Q
from sentry_sdk import capture_exception, capture_message
from spotipy.exceptions import SpotifyException
from requests.exceptions import HTTPError

from . import feed
from . import itunes
from . import podstat
from .spotify_api import spotify_api, fetch_all
from .experimental_spotify_podcast_api import experimental_spotify_podcast_api
from . import webtrekk
from .connection_meta import ConnectionMeta
from ..common.utils import (
    date_param,
    local_now,
    local_today,
    local_yesterday,
    date_range,
    BERLIN,
    UTC,
)
from ...models import (
    Podcast,
    PodcastITunesRating,
    PodcastITunesReview,
    PodcastEpisode,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataPodstat,
    PodcastDataSpotify,
    PodcastDataSpotifyHourly,
    PodcastDataWebtrekkPicker,
    PodcastEpisodeDataSpotifyPerformance,
    PodcastEpisodeDataWebtrekkPerformance,
    PodcastEpisodeDataSpotifyDemographics,
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
          None. If not set, 01-01-2016 is used.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None.
    """
    print("Running full scrape of", podcast)

    podcast_filter = Q(id=podcast.id)
    start_date = start_date or dt.date(2016, 1, 1)

    sleep(1)
    scrape_feed(podcast_filter=podcast_filter)

    sleep(1)
    scrape_itunes_reviews(podcast_filter=podcast_filter)

    sleep(1)
    scrape_spotify_experimental_performance(
        podcast_filter=podcast_filter,
    )

    sleep(1)
    scrape_spotify_experimental_demographics(
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
    scrape_podcast_data_webtrekk_picker(
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

    Results are saved to :class:`~okr.models.podcasts.PodcastEpisode`.

    Args:
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    # Fetch licensed podcasts and their names so we can match them to find
    # Spotify IDs of podcasts that were published on Spotify later
    licensed_podcasts = spotify_api.licensed_podcasts()
    spotify_podcasts = fetch_all(
        functools.partial(spotify_api.shows, market="DE"),
        list(
            uri.replace("spotify:show:", "")
            for uri in licensed_podcasts["shows"].keys()
        ),
        "shows",
    )

    for podcast in podcasts:
        try:
            _scrape_feed_podcast(podcast, spotify_podcasts)
        except Exception as e:
            print("Failed! Capturing exception and skipping.")
            capture_exception(e)


def _scrape_feed_podcast(podcast: Podcast, spotify_podcasts: List[Dict]):
    print("Scraping feed for", podcast)

    now = local_now()

    # Read data from RSS feed
    try:
        d = feed.parse(podcast.feed_url)
    except HTTPError as e:
        capture_message(
            f"RSS Feed for podcast {podcast} is not available (HTTP {e.response.status_code})."
        )
        podcast.episodes.update(available=False)
        return

    if len(d.entries) == 0:
        print(f"RSS Feed for Podcast {podcast} is empty.")
        capture_message(f"RSS Feed for podcast {podcast} is empty.")

    # Update podcast meta data
    podcast.name = d.feed.title
    podcast.author = d.feed.author
    podcast.image = d.feed.image.href
    podcast.description = d.feed.description
    podcast.itunes_category = d.feed.itunes_category
    podcast.itunes_subcategory = d.feed.itunes_subcategory
    podcast.save()

    # Attempt to find Spotify ID if there is none yet
    if not podcast.spotify_id:
        spotify_podcast_id = next(
            (p["id"] for p in spotify_podcasts if p and p["name"] == d.feed.title),
            None,
        )

        if spotify_podcast_id:
            print("Found new Spotify ID", spotify_podcast_id, "for", podcast)
            podcast.spotify_id = spotify_podcast_id
            podcast.save()

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
                podcast.spotify_id,
                episode_id,
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

    # Loop feed entries to find new episodes
    available_episode_ids = []
    for entry in d.entries:
        spotify_id = spotify_episode_id_by_name.get(entry.title)

        media_url = entry.enclosures[0].href
        zmdb_id = int(media_url.split("/")[-2])

        if "itunes_duration" in entry:
            t = dt.datetime.strptime(entry.itunes_duration, "%H:%M:%S")
            duration = dt.timedelta(
                hours=t.hour,
                minutes=t.minute,
                seconds=t.second,
            )
        else:
            duration = dt.timedelta(seconds=0)

        publication_date_time = dt.datetime(*entry.published_parsed[:6], tzinfo=UTC)
        defaults = {
            "podcast": podcast,
            "title": entry.title,
            "description": entry.description,
            "publication_date_time": publication_date_time,
            "media": media_url,
            "spotify_id": spotify_id,
            "duration": duration,
            "available": True,
            "last_available_date_time": now,
        }

        try:
            obj, created = PodcastEpisode.objects.update_or_create(
                zmdb_id=zmdb_id,
                defaults=defaults,
            )
            available_episode_ids.append(obj.id)
        except IntegrityError as e:
            capture_exception(e)
            print(
                f"Data for {entry.title} failed integrity check:",
                defaults,
                sep="\n",
            )

    podcast.episodes.exclude(id__in=available_episode_ids).update(
        available=False,
    )


def scrape_itunes_reviews(podcast_filter: Optional[Q] = None):
    """Read and process reviews data from the iTunes podcast library.

    This function retrieves two kinds of data for a podcast:

    1. Ratings: Star ratings (1 to 5 stars) left by users.
    2. Reviews: Written statements by users. These reviews also include a star rating.

    Ratings are saved to :class:`~okr.models.podcasts.PodcastITunesRating`.
    Reviews are saved to :class:`~okr.models.podcasts.PodcastITunesReview`.

    Args:
        podcast_filter (Optional[Q], optional): [description]. Defaults to None.
    """

    podcasts = Podcast.objects.all()

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        try:
            _scrape_itunes_reviews_podcast(podcast)
            sleep(4)
        except Exception as e:
            print("Failed! Capturing exception and skipping.")
            capture_exception(e)


def _scrape_itunes_reviews_podcast(podcast):
    itunes_data = itunes.get_reviews(podcast)

    if itunes_data is None:
        capture_message(f"Podcast {podcast.name} has no itunes_url or no ratings")
        return

    itunes_ratings, itunes_reviews = itunes_data

    PodcastITunesRating.objects.update_or_create(
        podcast=podcast,
        date=local_today(),
        defaults=itunes_ratings,
    )

    for author, data in itunes_reviews.items():
        PodcastITunesReview.objects.update_or_create(
            podcast=podcast,
            author=author,
            defaults=data,
        )


def scrape_spotify_api(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Read and process data from Spotify API.

    Supplies two kinds of Spotify-related data:

    a) Data about the podcast itself, such as the current number of the podcast's
    followers.

    b) Client side usage data for each podcast episode. This includes starts, streams
    (minimum listening duration of 1 minute), or listeners (number of accounts).

    Results are saved in :class:`~okr.models.podcasts.PodcastDataSpotify`,
    :class:`~okr.models.podcasts.PodcastDataSpotifyHourly`, and
    :class:`~okr.models.podcasts.PodcastEpisodeDataSpotify`.

    Args:
        start_date (dt.date, optional): Earliest date to request data for. Defaults to
          None. If not set, "6 days ago" is used.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None. If not set, "yesterday" is used.
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    yesterday = local_yesterday()

    if start_date is None:
        start_date = yesterday - dt.timedelta(days=5)

    end_date = end_date or yesterday

    podcasts = Podcast.objects.exclude(spotify_id=None)

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        try:
            _scrape_spotify_api_podcast(podcast, start_date, end_date)
        except Exception as e:
            print("Failed! Capturing exception and skipping.")
            capture_exception(e)

        gc.collect()


def _scrape_spotify_api_podcast(
    podcast: Podcast,
    start_date: dt.date,
    end_date: dt.date,
):
    print("Scraping spotify API for", podcast)

    # Retrieve follower for podcast from experimental API
    follower_data = experimental_spotify_podcast_api.podcast_followers(
        podcast.spotify_id,
        start=start_date,
        end=end_date,
    )
    # Transform to date-based dict
    follower_data = {
        dt.date.fromisoformat(item["date"]): item["count"]
        for item in follower_data["counts"]
    }

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

        defaults["followers"] = follower_data[date]

        PodcastDataSpotify.objects.update_or_create(
            podcast=podcast,
            date=date,
            defaults=defaults,
        )

        # Read hourly data
        if date < dt.date(2019, 12, 1):
            continue

        for hour in range(0, 24):
            agg_type_data = {}
            date_time = dt.datetime(date.year, date.month, date.day, hour, tzinfo=UTC)
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
    last_available_cutoff = local_today() - dt.timedelta(days=5)

    for podcast_episode in podcast.episodes.exclude(spotify_id=None).filter(
        Q(available=True) | Q(last_available_date_time__gt=last_available_cutoff)
    ):
        print("Scraping spotify episode data for", podcast_episode)

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


def scrape_spotify_experimental_performance(
    *,
    podcast_filter: Optional[Q] = None,
):
    """Request performance data for podcast episodes.

    Results are saved in
    :class:`~okr.models.podcasts.PodcastEpisodeDataSpotifyPerformance`.

    Args:
        podcast_filter (Optional[Q], optional): Filter to define a subset of data.
            Defaults to None.
    """
    today = local_today()

    podcasts = Podcast.objects.exclude(spotify_id=None)

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        try:
            _scrape_spotify_experimental_performance_podcast(podcast, today)
        except Exception as e:
            print("Failed! Capturing exception and skipping.")
            capture_exception(e)


def _scrape_spotify_experimental_performance_podcast(
    podcast: Podcast,
    today: dt.date,
):
    print(
        "Scraping spotify performance data for",
        podcast,
        "from experimental API",
    )

    last_available_cutoff = local_today() - dt.timedelta(days=5)

    for podcast_episode in podcast.episodes.exclude(spotify_id=None).filter(
        Q(available=True) | Q(last_available_date_time__gt=last_available_cutoff)
    ):
        print(
            "Scraping spotify episode performance data for",
            podcast_episode,
            "from experimental API",
        )

        try:
            performance_data = experimental_spotify_podcast_api.episode_performance(
                podcast_episode.spotify_id
            )

        except HTTPError as e:
            if e.response.status_code == 404:
                print("(404) No data found for", podcast_episode)
                continue

            raise

        average_listen = dt.timedelta(
            seconds=performance_data["medianCompletion"]["seconds"],
        )

        PodcastEpisodeDataSpotifyPerformance.objects.update_or_create(
            episode=podcast_episode,
            date=today,
            defaults=dict(
                average_listen=average_listen,
                quartile_1=performance_data["percentiles"]["25"],
                quartile_2=performance_data["percentiles"]["50"],
                quartile_3=performance_data["percentiles"]["75"],
                complete=performance_data["percentiles"]["100"],
            ),
        )


def scrape_spotify_experimental_demographics(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Request demographic data for podcast episodes.

    Results are saved in
    :class:`~okr.models.podcasts.PodcastEpisodeDataSpotifyDemographics`.

    Args:
        start_date (Optional[dt.date], optional): Earliest date to request data for.
            Defaults to None.
        end_date (Optional[dt.date], optional): Most recent date to request data for.
            Defaults to None.
        podcast_filter (Optional[Q], optional): Filter to define a subset of data.
            Defaults to None.
    """
    today = local_today()
    yesterday = local_yesterday()
    default_start = today - dt.timedelta(days=2)

    start_date = date_param(
        start_date,
        default=default_start,
        earliest=default_start,
        latest=yesterday,
    )
    end_date = date_param(
        end_date,
        default=yesterday,
        earliest=start_date,
        latest=yesterday,
    )

    podcasts = Podcast.objects.exclude(spotify_id=None)

    if podcast_filter:
        podcasts = podcasts.filter(podcast_filter)

    for podcast in podcasts:
        try:
            _scrape_spotify_experimental_demographics_podcast(
                podcast,
                start_date,
                end_date,
            )
        except Exception as e:
            print("Failed! Capturing exception and skipping.")
            capture_exception(e)


def _scrape_spotify_experimental_demographics_podcast(
    podcast: Podcast,
    start_date: dt.date,
    end_date: dt.date,
):
    print(
        "Scraping spotify demographics data for",
        podcast,
        "from experimental API",
    )

    first_episode_date = podcast.episodes.order_by("publication_date_time")[
        0
    ].publication_date_time.date()

    if start_date < first_episode_date:
        start_date = first_episode_date

    last_available_cutoff = local_today() - dt.timedelta(days=5)

    for podcast_episode in podcast.episodes.exclude(spotify_id=None).filter(
        Q(available=True) | Q(last_available_date_time__gt=last_available_cutoff)
    ):
        for date in reversed(date_range(start_date, end_date)):
            print(
                "Scraping spotify episode demographics data for",
                podcast_episode,
                "from experimental API",
            )

            try:
                aggregate_data = experimental_spotify_podcast_api.episode_aggregate(
                    podcast_episode.spotify_id,
                    start=date,
                )

            except HTTPError as e:
                if e.response.status_code == 404:
                    print("(404) No data found for", podcast_episode)
                    continue

                raise

            for age_range, age_range_data in aggregate_data["ageFacetedCounts"].items():
                for gender, gender_data in age_range_data["counts"].items():

                    PodcastEpisodeDataSpotifyDemographics.objects.update_or_create(
                        episode=podcast_episode,
                        date=date,
                        age_range=PodcastEpisodeDataSpotifyDemographics.AgeRange(
                            age_range
                        ),
                        gender=PodcastEpisodeDataSpotifyDemographics.Gender(gender),
                        defaults=dict(
                            count=gender_data,
                        ),
                    )


def scrape_podstat(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Read and process data from Podstat.

    Supplies data per episode of self hosted podcasts. Specifically, the number of
    download and on-demand client requests per media file for each episode.

    Results are saved in :class:`~okr.models.podcasts.PodcastEpisodeDataPodstat`.

    Args:
        start_date (dt.date, optional): Earliest date to request data for. Defaults to
          None. If not set, "20 days ago" is used.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None. If not set, "today" is used.
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
            try:
                _scrape_podstat_podcast(
                    connection_meta,
                    podcast,
                    start_time,
                    end_time,
                )
            except Exception as e:
                print("Failed! Capturing exception and skipping.")
                capture_exception(e)

        del connection_meta
        gc.collect()


def _scrape_podstat_podcast(
    connection_meta: ConnectionMeta,
    podcast: Podcast,
    start_time: dt.datetime,
    end_time: dt.datetime,
):
    print("Scraping podstat for", podcast)

    last_available_cutoff = local_today() - dt.timedelta(days=10)

    for podcast_episode in podcast.episodes.filter(
        Q(available=True) | Q(last_available_date_time__gt=last_available_cutoff)
    ):
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


def scrape_podcast_data_webtrekk_picker(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Read and process data from Webtrekk.

    Supplies Podcast Picker usage data from the Webtrekk database.

    Results are saved in
    :class:`~okr.models.podcasts.PodcastDataWebtrekkPicker`.

    Args:
        start_date (dt.date, optional): Earliest date to request data for. Defaults to
          None. If not set, "3 days ago" is used. Values are truncated to be no longer
          than 7 days ago.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None. If not set, "yesterday" is used.
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    today = local_today()
    yesterday = local_yesterday()

    start_date = date_param(
        start_date,
        default=yesterday - dt.timedelta(days=2),
        earliest=today - dt.timedelta(days=7),
        latest=yesterday,
    )
    end_date = date_param(
        end_date,
        default=yesterday,
        earliest=start_date,
        latest=yesterday,
    )

    for date in reversed(date_range(start_date, end_date)):
        data = webtrekk.cleaned_picker_data(date)

        podcasts = Podcast.objects.all()

        if podcast_filter:
            podcasts = podcasts.filter(podcast_filter)

        for podcast in podcasts:
            normalized_name = webtrekk.normalize_name(podcast.name)
            if normalized_name not in data:
                continue

            PodcastDataWebtrekkPicker.objects.update_or_create(
                date=date, podcast=podcast, defaults=data[normalized_name]
            )
        print(f"Finished scraping of Webtrekk performance data for {date}.")


def scrape_episode_data_webtrekk_performance(
    *,
    start_date: Optional[dt.date] = None,
    end_date: Optional[dt.date] = None,
    podcast_filter: Optional[Q] = None,
):
    """Read and process data from Webtrekk.

    Supplies episode data from the Webtrekk database based on each episode's ZMDB ID.

    Results are saved in
    :class:`~okr.models.podcasts.PodcastEpisodeDataWebtrekkPerformance`.

    Args:
        start_date (dt.date, optional): Earliest date to request data for. Defaults to
          None. If not set, "3 days ago" is used. Values are truncated to be no longer
          than 7 days ago.
        end_date (dt.date, optional): Latest date to request data for. Defaults to
          None. If not set, "yesterday" is used.
        podcast_filter (Q, optional): Filter for a subset of all Podcast objects.
          Defaults to None.
    """
    today = local_today()
    yesterday = local_yesterday()

    start_date = date_param(
        start_date,
        default=yesterday - dt.timedelta(days=2),
        earliest=today - dt.timedelta(days=7),
        latest=yesterday,
    )
    end_date = date_param(
        end_date,
        default=yesterday,
        earliest=start_date,
        latest=yesterday,
    )

    for date in reversed(date_range(start_date, end_date)):
        data = webtrekk.cleaned_audio_data(date)

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
