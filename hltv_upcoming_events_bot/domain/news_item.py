import datetime
from dataclasses import dataclass


@dataclass
class NewsItem(object):
    date_time_utc: datetime.datetime
    title: str
    short_desc: str
    url: str
    comment_count: int
    comment_avg_hour: float

    def __hash__(self):
        return hash(self.url)
