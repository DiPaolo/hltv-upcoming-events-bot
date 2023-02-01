import datetime
from dataclasses import dataclass
from typing import List

from hltv_upcoming_events_bot.domain.match_stars import MatchStars
from hltv_upcoming_events_bot.domain.match_state import MatchState
from hltv_upcoming_events_bot.domain.team import Team
from hltv_upcoming_events_bot.domain.tournament import Tournament
from hltv_upcoming_events_bot.domain.translation import Translation


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
