from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import users_db_functions


def get_keyboard(answers: list, is_multians=False):
    multi = 'multi' if is_multians else ''
    buttons = [
        InlineKeyboardButton(text=answer, callback_data=f'{multi}ans_{index}')
        for index, answer in enumerate(answers)
    ]
    if is_multians:
        buttons += [InlineKeyboardButton(text='Confirm', callback_data='multians_confirm')]

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(*buttons)

    return kb


async def get_product_keyboard(user_id: int, product: dict):
    product_keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='Previous', callback_data='product_previous'),
        InlineKeyboardButton(text='Next', callback_data='product_next'),
    )
    favourites = users_db_functions.get_users_favourite(user_id=user_id)
    print('favourites', favourites)
    if product not in favourites:
        product_keyboard.add(InlineKeyboardButton(text='Add to liked', callback_data='product_like'))
    else:
        product_keyboard.add(InlineKeyboardButton(text='Remove form liked', callback_data='product_unlike'))
    return product_keyboard


def get_scale_keyboard():
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton(text='Yes', callback_data='scale_1'),
        InlineKeyboardButton(text='Dont know', callback_data='scale_0.5'),
        InlineKeyboardButton(text='No', callback_data='scale_0')
    ).add(
        InlineKeyboardButton(text='Get products', callback_data='scale_getproducts')
    )
