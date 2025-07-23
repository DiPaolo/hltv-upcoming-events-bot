import logging
from enum import Enum

_logger = logging.getLogger('hltv_upcoming_events_bot.domain')


class GameType(Enum):
    UNKNOWN = (0, 'Unknown')
    CS2 = (1, 'CS2')
    DOTA2 = (2, 'Dota 2')

    def __str__(self):
        return self.value[1]

#
# _GAME_TYPE_NAMES = {
#     GameType.CS2: 'CS2',
#     GameType.DOTA2: 'Dota 2'
# }


# def get_game_type_name(game_type: GameType) -> str:
#     if game_type in _GAME_TYPE_NAMES:
#         return _GAME_TYPE_NAMES[game_type]
#
#     _logger.error(f'Failed to get game type name (game_type={game_type}): unmapped value')
#     return _GAME_TYPE_NAMES[GameType.UNKNOWN]


# def get_game_type_by_name(name: str) -> GameType:
#     for key, value in _GAME_TYPE_NAMES.items():
#         if value == name:
#             return key
#
#     _logger.error(f'Failed to get game type by name (name={name}): no such element found')
#     return GameType.UNKNOWN
