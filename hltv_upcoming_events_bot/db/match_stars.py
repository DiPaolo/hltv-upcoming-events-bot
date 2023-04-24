from enum import Enum
import hltv_upcoming_events_bot.domain as domain


class MatchStars(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    @staticmethod
    def from_domain_object(domain_obj: domain.MatchStars):
        return MatchStars(domain_obj.value)

    def to_domain_object(self):
        return domain.MatchStars(self.value)
