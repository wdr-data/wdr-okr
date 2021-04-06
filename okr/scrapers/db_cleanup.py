import os
import datetime as dt

from loguru import logger

from ..models import (
    # Podcasts
    PodcastDataSpotify,
    PodcastDataSpotifyHourly,
    PodcastEpisodeDataPodstat,
    PodcastEpisodeDataSpotify,
    PodcastEpisodeDataSpotifyDemographics,
    PodcastEpisodeDataSpotifyPerformance,
    PodcastEpisodeDataWebtrekkPerformance,
    # Pages
    PropertyDataGSC,
    PropertyDataQueryGSC,
    PageDataGSC,
    PageDataQueryGSC,
    PageDataWebtrekk,
)


def run_db_cleanup():
    # Only run on Heroku staging deployment
    if os.environ.get("HEROKU_APP_NAME") != "wdr-okr-staging":
        return

    max_age = dt.timedelta(days=45)
    cutoff = dt.date.today() - max_age

    purge_models = [
        # Podcasts
        PodcastDataSpotify,
        PodcastDataSpotifyHourly,
        PodcastEpisodeDataPodstat,
        PodcastEpisodeDataSpotify,
        PodcastEpisodeDataSpotifyDemographics,
        PodcastEpisodeDataSpotifyPerformance,
        PodcastEpisodeDataWebtrekkPerformance,
        # Pages
        PropertyDataGSC,
        PropertyDataQueryGSC,
        PageDataGSC,
        PageDataQueryGSC,
        PageDataWebtrekk,
    ]

    date_field_names = ["date", "date_time"]

    for model in purge_models:
        date_field = None

        for date_field_name in date_field_names:
            try:
                date_field = getattr(model, date_field_name)
                break
            except AttributeError:
                continue

        if not date_field:
            logger.error(
                "date_field not found for model {} - tried: {}",
                model,
                date_field_names,
            )
            continue

        filter_kwargs = {f"{date_field.field.name}__lt": cutoff}

        result_set = model.objects.filter(**filter_kwargs)
        logger.info(
            "Deleting {delete_count} out of {total_count} items from {model}",
            delete_count=result_set.count(),
            total_count=model.objects.count(),
            model=model,
        )
        result_set.delete()
        logger.success("DB cleanup complete.")
