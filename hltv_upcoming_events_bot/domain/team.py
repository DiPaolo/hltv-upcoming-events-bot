from dataclasses import dataclass


@dataclass
class Team(object):
    name: str
    url: str = None
