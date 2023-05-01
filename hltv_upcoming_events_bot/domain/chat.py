from dataclasses import dataclass


@dataclass
class Chat(object):
    telegram_id: int
    title: str
    type: str
