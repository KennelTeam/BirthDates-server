from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(Helper):
    mode = HelperMode.snake_case

    WAITING_KEYWORDS = ListItem()
    WAITING_TREE_SELECT = ListItem()
