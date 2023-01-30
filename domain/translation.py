from dataclasses import dataclass
from domain.language import Language


@dataclass
class Translation(object):
    streamer_name: str
    language: Language
    url: str
