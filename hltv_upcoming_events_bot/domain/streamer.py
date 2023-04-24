from dataclasses import dataclass


@dataclass
class Streamer(object):
    name: str
    language: str
    url: str
