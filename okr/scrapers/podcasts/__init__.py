from datetime import datetime, timedelta
import pytz

from django.db.utils import IntegrityError

from . import feed
from . import spotify
from . import podstat
from ...models import Podcast, PodcastEpisode

def scrape():
    for podcast in Podcast.objects.all():
        d = feed.parse(podcast.feed_url)
        for entry in d.entries:
            media_url = entry.enclosures[0].href
            zmdb_id = int(media_url.split('/')[-2])
            t = datetime.strptime(entry.itunes_duration, "%H:%M:%S")
            duration = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            publication_date_time = datetime(*entry.published_parsed[:6], tzinfo=pytz.UTC)
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
                    zmdb_id=zmdb_id,
                    defaults=defaults,
                )
            except IntegrityError:
                print(
                    f"Data for {entry.title} failed integrity check:",
                    defaults,
                    sep="\n",
                )
