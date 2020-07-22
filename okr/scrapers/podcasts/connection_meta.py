from collections import namedtuple

ConnectionMeta = namedtuple("Connection", ["engine", "session", "classes"])
