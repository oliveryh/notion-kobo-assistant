from enum import Enum


class NerdIcon(Enum):
    CHART_GANTT = 'ﭫ'
    CHECK = ''
    CLOCK = ''
    EXTERNAL_LINK = ''
    GMAIL = ''
    INFO = ''
    TRELLO = '僧'
    USER = ''
    WARNING = ''

    def __str__(self):
        return str(self.value)
