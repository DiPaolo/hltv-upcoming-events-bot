import datetime
from dataclasses import dataclass
from typing import List

from domain.match_stars import MatchStars
from domain.match_state import MatchState
from domain.team import Team
from domain.tournament import Tournament
from domain.translation import Translation


@dataclass
class Match(object):
    team1: Team
    team2: Team
    time_utc: datetime.datetime
    stars: MatchStars
    tournament: Tournament
    state: MatchState
    url: str
    translations: List[Translation]
