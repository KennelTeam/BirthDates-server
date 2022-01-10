from dataclasses import dataclass


@dataclass(frozen=True)
class CommandsConsts:
    START_COMMAND = 'Start bot'
    HELP_COMMAND = 'Get Help'
    KEYWORDS_ALGORITHM_COMMAND = 'Compare keywords algorithm'
    TREE_ALGORITHM_COMMAND = 'Tree algorithm'
    LIKED_COMMAND = 'Your liked products'
    BAYES_ALGORITHM_COMMAND = 'Bayes Algorithm'


@dataclass(frozen=True)
class MessagesConsts:
    START_MESSAGE = "Welcome! I will help you choose gift for your friend, wife/husband, child or for Donald Tramp, you just have to play a little game. "
    HELP_MESSAGE = 'help message...'
    LIKED_EMPTY_MESSAGE = 'Your liked products is empty'
    START_KEYWORDS_ALGORITHM_MESSAGE = 'Start "Compare Keywords" algorithm...'
    SELECT_KEYWORDS_MESSAGE = 'Select Keyword'
    START_TREE_ALGORITHM = 'Start "Tree" algorithm'
    START_BAYES_ALGORITHM = 'Start "Bayes" algorithm'


@dataclass(frozen=True)
class EmojiConsts:
    CHECK_MARK_EMOJI = '✅'


Commands = CommandsConsts()
Messages = MessagesConsts()
Emojis = EmojiConsts()
