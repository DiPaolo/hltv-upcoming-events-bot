import datetime
import logging
from typing import Optional
from hltv_upcoming_events_bot import db


def parse_timezone_offset_str(text: str) -> Optional[int]:
    try:
        int_value = int(text)
        if -12 <= int_value <= 14:
            return int_value
        else:
            logging.warning(f'Failed to parse timezone (text={text}, int_value={int_value}): value is out of valid range')
            return None
    except Exception as ex:
        logging.warning(f'Failed to parse timezone (text={text}): {ex}')
        return None


def set_user_timezone(user_tg_id: int, timezone_offset: int) -> Optional[datetime.timezone]:
    if not -12 <= timezone_offset <= 14:
        logging.warning(f'Failed to set timezone (user_tg_id={user_tg_id}, timezone_offset={timezone_offset}): '
                        f'value is out of valid range')
        return None

    try:
        timezone = datetime.timezone(datetime.timedelta(hours=timezone_offset))
    except Exception as ex:
        logging.error(f'Failed to set timezone (user_tg_id={user_tg_id}, timezone_offset={timezone_offset}): {ex}')
        return None

    utc_offset_minutes = timezone.utcoffset(None).seconds // 60
    user_timezone = db.add_user_timezone(user_tg_id, utc_offset_minutes)
    if user_timezone is None:
        logging.error(f'Failed to set timezone (user_tg_id={user_tg_id}, timezone_offset={timezone_offset}): '
                      f'failed to add data to DB')
        return None

    return timezone


def get_user_timezone(user_tg_id: int) -> Optional[datetime.timezone]:
    return None
