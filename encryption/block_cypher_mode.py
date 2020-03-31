from enum import Enum


class BlockCypherMode(Enum):
    ECB = 'ECB'
    CBC = 'CBC'
    CFB = 'CFB'
    OFB = 'OFB'
