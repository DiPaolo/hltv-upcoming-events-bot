import datetime
from dataclasses import dataclass

from .match_stars import MatchStars
from .match_state import MatchState
from .team import Team
from .tournament import Tournament


@dataclass
class Match(object):
    team1: Team
    team2: Team
    time_utc: datetime.datetime
    stars: MatchStars
    tournament: Tournament
    state: MatchState
    url: str
