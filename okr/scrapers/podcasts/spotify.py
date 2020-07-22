import os
import functools
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, defer, undefer, joinedload, relationship
from sqlalchemy.ext.automap import automap_base

from .connection_meta import ConnectionMeta


@contextmanager
def make_connection_meta():
    engine = create_engine(
        f"mysql://{os.environ['MYSQL_PODCAST_USER']}:{os.environ['MYSQL_PODCAST_PASSWORD']}@{os.environ['MYSQL_PODCAST_HOST']}/{os.environ['MYSQL_PODCAST_DATABASE_SPOTIFY']}"
    )
    session = Session(engine)

    Base = automap_base()
    Base.prepare(engine, reflect=True)

    class classes:
        Podcast = Base.classes.podcasts
        Episode = Base.classes.episodes
        Stream = Base.classes.episode_data_streams
        Additional = Base.classes.episode_data_additional

    try:
        yield ConnectionMeta(engine=engine, session=session, classes=classes)
    finally:
        session.close()


def get_podcast(connection_meta, name):
    Podcast = connection_meta.classes.Podcast

    return connection_meta.session.query(Podcast).filter(Podcast.podcast == name)[0]

    """
    print(podcast.podcast, "\n")

    for episode in podcast.episodes_collection:
        print(episode.episode)
        for stream in episode.episode_data_streams_collection:
            print(vars(stream))
    """


if __name__ == "__main__":
    get_podcast("WDR 5 Polit-WG")
