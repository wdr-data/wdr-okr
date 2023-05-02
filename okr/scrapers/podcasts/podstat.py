"""Wrapper for Podstat API."""

import os
from contextlib import contextmanager
from typing import Iterator, List

from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import Session, joinedload, relationship
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import DeclarativeMeta

from .connection_meta import ConnectionMeta


@contextmanager
def make_connection_meta() -> Iterator[ConnectionMeta]:
    """Connect to Podstat database.

    Yields:
        Iterator[ConnectionMeta]: ConnectionMeta object.
    """
    engine = create_engine(
        f"mariadb+mariadbconnector://{os.environ['MYSQL_PODCAST_USER']}:{os.environ['MYSQL_PODCAST_PASSWORD']}@{os.environ['MYSQL_PODCAST_HOST']}/{os.environ['MYSQL_PODCAST_DATABASE_PODSTAT']}",
        connect_args={"ssl": True, "ssl_verify_cert": False},
    )
    session = Session(engine)

    Base = automap_base()

    class classes:
        """Classes for connection to Podstat API."""

        class PodcastCount(Base):
            """Class for podcast count."""

            __tablename__ = "podcast_ucount_tag"
            urlid = Column(Integer, ForeignKey("podcast_url.urlid"), primary_key=True)

        class PodcastMediaUrl(Base):
            """Class for media URL of podcast."""

            __tablename__ = "podcast_murl"
            podcast_url_collection = relationship(
                "PodcastUrl",
                backref="podcast_murl",
                viewonly=True,
                sync_backref=False,
                lazy="joined",
            )

        class PodcastUrl(Base):
            """Class for podcast URL."""

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
            """Class for podcast media count."""

            __tablename__ = "podcast_mucount_tag"

    Base.prepare(engine, reflect=True)

    try:
        yield ConnectionMeta(engine=engine, session=session, classes=classes)
    finally:
        session.expire_all()
        session.close()
        del session
        del engine


def get_episode(connection_meta: ConnectionMeta, zmdb_id: int) -> List[DeclarativeMeta]:
    """Retrieve Podstat data for zmdb_id.

    Args:
        connection_meta (ConnectionMeta): Connection to Podstat database.
        zmdb_id (int): ZMDB ID

    Returns:
        list[DeclarativeMeta]: List of data sets that match zmdb_id.
    """

    PodcastUrl = connection_meta.classes.PodcastUrl
    # Actually returns (hopefully) 2 items, one for ondemand and one for downloads
    query = (
        connection_meta.session.query(PodcastUrl)
        # Use FULLTEXT index to search for the zmdb_id first
        .filter(PodcastUrl.titel.match(str(zmdb_id)))
        # Then make sure it's at the end of the string
        .having(PodcastUrl.titel.like(f"% {zmdb_id}")).options(
            # Prevents insane RAM usage due to DB weirdness
            joinedload(PodcastUrl.podcast_murl)
        )
    )

    return list(query)
