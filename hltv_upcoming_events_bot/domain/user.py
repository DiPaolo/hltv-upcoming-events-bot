from dataclasses import dataclass


@dataclass
class User(object):
    telegram_id: int
    username: str
    first_name: str
    last_name: str
    is_bot: bool
    is_premium: bool
    language_code: str
