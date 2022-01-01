from enum import Enum


class Medium(Enum):
    OTHER = 0
    ARTICLE = 1
    VIDEO = 2
    BOOK = 3


class Status(Enum):
    TODO = 0
    PENDING = 1
    COMPLETE = 2
