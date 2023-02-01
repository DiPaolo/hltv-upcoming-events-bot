from enum import Enum
import hltv_upcoming_events_bot.domain.match_stars


class MatchStars(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    @staticmethod
    def from_domain_object(domain_obj: hltv_upcoming_events_bot.domain.match_stars.MatchStars):
        return MatchStars(domain_obj.value)
