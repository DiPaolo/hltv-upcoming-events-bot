from enum import Enum


class RetCode(Enum):
    OK = 1
    ERROR = 2
    NOT_EXIST = 3
    ALREADY_EXIST = 4
