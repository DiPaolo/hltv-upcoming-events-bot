from dataclasses import dataclass


@dataclass
class Tournament(object):
    name: str = ''
    url: str = ''
    hltv_id: int = -1
