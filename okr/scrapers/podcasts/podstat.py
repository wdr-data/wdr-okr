import os
import functools
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.automap import automap_base

from .connection_meta import ConnectionMeta


@contextmanager
def make_connection_meta() -> Iterator[ConnectionMeta]:
    """Connect to Podstat database.

    Yields:
        Iterator[ConnectionMeta]: ConnectionMeta object.
    """
    engine = create_engine(
        f"mysql://{os.environ['MYSQL_PODCAST_USER']}:{os.environ['MYSQL_PODCAST_PASSWORD']}@{os.environ['MYSQL_PODCAST_HOST']}/{os.environ['MYSQL_PODCAST_DATABASE_PODSTAT']}"
    )
    session = Session(engine)

    Base = automap_base()

    class classes:
        class PodcastCount(Base):
            __tablename__ = "podcast_ucount_tag"
            urlid = Column(Integer, ForeignKey("podcast_url.urlid"), primary_key=True)

        class PodcastMediaUrl(Base):
            __tablename__ = "podcast_murl"
            podcast_url_collection = relationship(
                "PodcastUrl",
                backref="podcast_murl",
                viewonly=True,
                sync_backref=False,
                lazy="joined",
            )

        class PodcastUrl(Base):
            __tablename__ = "podcast_url"

            murlid = Column(Integer, ForeignKey("podcast_murl.murlid"))
            podcast_ucount_tag_collection = relationship(
                "PodcastCount",
                backref="podcast_url",
                viewonly=True,
                sync_backref=False,
                lazy="dynamic",
            )

        class PodcastMediaCount(Base):
            __tablename__ = "podcast_mucount_tag"

    Base.prepare(engine, reflect=True)

    try:
        yield ConnectionMeta(engine=engine, session=session, classes=classes)
    finally:
        session.expire_all()
        session.close()
        del session
        del engine


def get_episode(connection_meta: ConnectionMeta, zmdb_id: int) -> list:
    """Retrieve Podstat data for zmdb_id.

    Args:
        connection_meta (ConnectionMeta): Connection to Podstat database.
        zmdb_id (int): ZMDB ID

    Returns:
        list: List of data sets that match zmdb_id.
    """

    PodcastUrl = connection_meta.classes.PodcastUrl
    # Actually returns (hopefully) 2 items, one for ondemand and one for downloads
    return list(
        connection_meta.session.query(PodcastUrl).filter(
            PodcastUrl.titel.like(f"% {zmdb_id}")
        )
    )

    """
    print(podcast.titel, "\n")
    print(vars(podcast), "\n")
    print(vars(podcast.podcast_murl), "\n")
    print("Found", len(podcast.podcast_ucount_tag_collection), "ucounts")

    for day_data in podcast.podcast_ucount_tag_collection:
        print(vars(day_data))
    """


if __name__ == "__main__":
    get_podcast(1505468)
