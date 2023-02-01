from dataclasses import dataclass
from hltv_upcoming_events_bot.domain.language import Language


@dataclass
class Translation(object):
    streamer_name: str
    language: Language
    url: str
