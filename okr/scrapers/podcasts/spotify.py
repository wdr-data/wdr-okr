import os
import functools
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.automap import automap_base

from .connection_meta import ConnectionMeta


@contextmanager
def make_connection_meta():
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
