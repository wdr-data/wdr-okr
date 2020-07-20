import os
import functools

from sqlalchemy import create_engine, Column, Integer, ForeignKey
from sqlalchemy.orm import Session, defer, undefer, joinedload, relationship, foreign
from sqlalchemy.ext.automap import automap_base


engine = None


def requires_engine(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global engine
        if not engine:
            engine = create_engine(
                f"mysql://{os.environ['MYSQL_PODCAST_USER']}:{os.environ['MYSQL_PODCAST_PASSWORD']}@{os.environ['MYSQL_PODCAST_HOST']}/{os.environ['MYSQL_PODCAST_DATABASE_PODSTAT']}"
            )
        return func(*args, **kwargs)

    return wrapper


@requires_engine
def get_podcast(zmdb_id):
    Base = automap_base()

    class PodcastCount(Base):
        __tablename__ = "podcast_ucount_tag"
        urlid = Column(Integer, ForeignKey("podcast_url.urlid"))

    class PodcastMediaUrl(Base):
        __tablename__ = "podcast_murl"
        podcast_url_collection = relationship(
            "PodcastUrl", backref="podcast_murl", viewonly=True, sync_backref=False
        )

    class PodcastUrl(Base):
        __tablename__ = "podcast_url"

        murlid = Column(Integer, ForeignKey("podcast_murl.murlid"))
        podcast_ucount_tag_collection = relationship(
            "PodcastCount", backref="podcast_url", viewonly=True, sync_backref=False
        )

    Base.prepare(engine, reflect=True)

    PodcastMediaCount = Base.classes.podcast_mucount_tag

    session = Session(engine)

    podcast = session.query(PodcastUrl).filter(PodcastUrl.titel.like(f"%{zmdb_id}"))[1]
    # return podcast

    print(podcast.titel, "\n")
    print(vars(podcast), "\n")
    print(vars(podcast.podcast_murl), "\n")
    print("Found", len(podcast.podcast_ucount_tag_collection), "ucounts")

    return
    for day_data in podcast.podcast_ucount_tag_collection:
        print(vars(day_data))


if __name__ == "__main__":
    get_podcast(1505468)
