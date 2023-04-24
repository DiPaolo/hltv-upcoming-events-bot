from dataclasses import dataclass
from .match import Match
from .streamer import Streamer


@dataclass
class Translation(object):
    match: Match
    streamer: Streamer
