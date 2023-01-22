import datetime
from dataclasses import dataclass

from domain.match_stars import MatchStars
from domain.team import Team


@dataclass
class Match(object):
    team1: Team
    team2: Team
    time_utc: datetime.datetime
    # stars: MatchStars
    url: str
