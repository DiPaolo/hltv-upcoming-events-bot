import datetime
import logging
from typing import Optional

import hltv_upcoming_events_bot.service.db as db_service

_logger = logging.getLogger('hltv_upcoming_events_bot.service.timezone')


def parse_timezone_offset_str(text: str) -> Optional[int]:
    try:
        int_value = int(text)
        if -12 <= int_value <= 14:
            return int_value
        else:
            _logger.warning(
                f'Failed to parse timezone (text={text}, int_value={int_value}): value is out of valid range')
            return None
    except Exception as ex:
        _logger.warning(f'Failed to parse timezone (text={text}): {ex}')
        return None


def set_user_timezone(user_tg_id: int, timezone_offset: int) -> Optional[datetime.timezone]:
    if not -12 <= timezone_offset <= 14:
        _logger.warning(f'Failed to set timezone (user_tg_id={user_tg_id}, timezone_offset={timezone_offset}): '
                        f'value is out of valid range')
        return None

    try:
        timezone = datetime.timezone(datetime.timedelta(hours=timezone_offset))
    except Exception as ex:
        _logger.error(f'Failed to set timezone (user_tg_id={user_tg_id}, timezone_offset={timezone_offset}): {ex}')
        return None

    utc_offset_minutes = timezone.utcoffset(None).seconds // 60
    user_timezone = db_service.add_user_timezone(user_tg_id, utc_offset_minutes)
    if user_timezone is None:
        _logger.error(f'Failed to set timezone (user_tg_id={user_tg_id}, timezone_offset={timezone_offset}): '
                      f'failed to add data to DB')
        return None

    return timezone


def get_user_timezone(user_tg_id: int) -> Optional[datetime.timezone]:
    timezone = db_service.get_user_timezone(user_tg_id)
    if timezone is None:
        # use server's timezone as default
        timezone = datetime.datetime.now().astimezone().tzinfo

    return timezone
