from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(Helper):
    mode = HelperMode.snake_case
    NONE = ListItem()
    WAITING_KEYWORDS = ListItem()
    STATE_2 = ListItem()
