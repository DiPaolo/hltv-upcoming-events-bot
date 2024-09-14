import logging
from enum import Enum
from typing import List

_logger = logging.getLogger('hltv_upcoming_events_bot.domain')


class MatchState(Enum):
    UNKNOWN = 0
    PLANNED = 1
    DELAYED = 2
    RUNNING = 3
    FINISHED = 4


_MATCH_STATE_NAMES_ENG = {
    MatchState.UNKNOWN: 'Unknown',
    MatchState.PLANNED: 'Planned',
    MatchState.DELAYED: 'Delayed',
    MatchState.RUNNING: 'Running',
    MatchState.FINISHED: 'Finished'
}


def get_match_state_name(state: MatchState) -> str:
    if state in _MATCH_STATE_NAMES_ENG:
        return _MATCH_STATE_NAMES_ENG[state]

    _logger.error(f'Failed to get match state name for match state (={state}): no such element found')
    return _MATCH_STATE_NAMES_ENG[MatchState.UNKNOWN]


def get_match_state_by_name(name: str) -> MatchState:
    for key, value in _MATCH_STATE_NAMES_ENG.items():
        if value == name:
            return key

    _logger.error(f'Failed to get match state by name (={name}): no such element found')
    return MatchState.UNKNOWN


def get_all_match_state_names() -> List[str]:
    return [item for item in _MATCH_STATE_NAMES_ENG.values()]
