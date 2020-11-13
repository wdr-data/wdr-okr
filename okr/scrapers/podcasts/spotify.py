"""Wrapper for Podstat Spotify API
"""

import os
import functools
from contextlib import contextmanager
from typing import Iterator, List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from .connection_meta import ConnectionMeta


@contextmanager
def make_connection_meta() -> Iterator[ConnectionMeta]:
    """Connect to Podstat Spotify API.

    Yields:
        Iterator[ConnectionMeta]: ConnectionMeta object.
    """
    engine = create_engine(
        f"mysql://{os.environ['MYSQL_PODCAST_USER']}:{os.environ['MYSQL_PODCAST_PASSWORD']}@{os.environ['MYSQL_PODCAST_HOST']}/{os.environ['MYSQL_PODCAST_DATABASE_SPOTIFY']}"
    )
    session = Session(engine)

    Base = automap_base()

    class classes:
        class Episode(Base):
            __tablename__ = "episodes"

            episode_data_streams_collection = relationship(
                "episode_data_streams",
                lazy="dynamic",
            )

            episode_data_additional_collection = relationship(
                "episode_data_additional",
                lazy="dynamic",
            )

        class Podcast(Base):
            __tablename__ = "podcasts"

            episodes_collection = relationship(
                "Episode",
                lazy="dynamic",
            )
            podcasts_follower_collection = relationship(
                "podcasts_follower",
                lazy="dynamic",
            )

    Base.prepare(engine, reflect=True)

    classes.Stream = Base.classes.episode_data_streams
    classes.Additional = Base.classes.episode_data_additional
    classes.FollowersData = Base.classes.podcasts_follower

    try:
        yield ConnectionMeta(engine=engine, session=session, classes=classes)
    finally:
        session.expire_all()
        session.close()
        del session
        del engine


def get_podcast(connection_meta: ConnectionMeta, name: str) -> DeclarativeMeta:
    """Retrieve podcast data from API.

    Args:
        connection_meta (ConnectionMeta): Connection to API.
        name (str): Name of podcast to look for.

    Returns:
        DeclarativeMeta: The podcast matching the name.
    """
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
