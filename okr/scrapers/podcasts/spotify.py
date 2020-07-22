import os
import functools
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, defer, undefer, joinedload, relationship
from sqlalchemy.ext.automap import automap_base


engine = None


def requires_engine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global engine
        if not engine:
            engine = create_engine(
                f"mysql://{os.environ['MYSQL_PODCAST_USER']}:{os.environ['MYSQL_PODCAST_PASSWORD']}@{os.environ['MYSQL_PODCAST_HOST']}/{os.environ['MYSQL_PODCAST_DATABASE_SPOTIFY']}"
            )
        return func(*args, **kwargs)

    return wrapper


@contextmanager
@requires_engine
def get_podcast(name):
    Base = automap_base()
    Base.prepare(engine, reflect=True)

    Podcast = Base.classes.podcasts
    Episode = Base.classes.episodes
    Stream = Base.classes.episode_data_streams
    Additional = Base.classes.episode_data_additional

    session = Session(engine)

    podcast = session.query(Podcast).filter(Podcast.podcast == name)[0]

    try:
        yield podcast
    finally:
        session.close()

    """
    print(podcast.podcast, "\n")

    for episode in podcast.episodes_collection:
        print(episode.episode)
        for stream in episode.episode_data_streams_collection:
            print(vars(stream))
    """


if __name__ == "__main__":
    get_podcast("WDR 5 Polit-WG")
