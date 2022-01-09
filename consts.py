from dataclasses import dataclass
from singleton import singleton


@singleton
@dataclass
class Messages:
    HELP_MESSAGE = 'help message...'
    START_MESSAGE = 'start message...'
    COMPARE_KEYWORD_START_MESSAGE = 'Start "Compare Keywords" algorithm...'
    TREE_START_MESSAGE = 'Start "Tree" algorithm'


@singleton
@dataclass
class Commands:
    START_COMMAND = 'Start bot'
    HELP_COMMAND = 'Get Help'
    KEYWORDS_ALGORITHMS_COMMAND = 'Compare keywords algorithm'
