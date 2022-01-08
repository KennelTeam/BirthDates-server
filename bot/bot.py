import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.builtin import Text

import messages
from compare_keywords import choose_gifts
from states import States
from config import get_token_from_dotenv

logging.basicConfig(level=logging.INFO)

bot = Bot(token=get_token_from_dotenv())
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())

check_mark_emoji = '✅'

dp.bot.set_my_commands([
    types.BotCommand('start', 'Start bot'),
    types.BotCommand('help', 'Get Help'),
    types.BotCommand('compare_keywords', 'Compare keywords algorithm'),
])


def get_product_text(product: dict):
    ...
    # name = product['name']
    # link = product['link']
    # return name + '\n' + link


async def show_product(user_id, products: list):
    product_index = 0
    product_keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='Previous', callback_data='product_previous'),
        InlineKeyboardButton(text='Next', callback_data='product_next'),
        InlineKeyboardButton(text='Add to liked', callback_data='product_like')
    )
    await bot.send_message(user_id, str(products[product_index]), reply_markup=product_keyboard)

    @dp.callback_query_handler(Text(startswith='product_'))
    async def product_actions_handler(query: CallbackQuery):
        nonlocal product_index
        action = query.data.split('_')[1]
        if action == 'like':
            print('like')
            # adding product to database...
            return
        change_num = 1 if action == 'next' else -1
        if 0 <= product_index + change_num < len(products):
            await query.message.edit_text(
                # text=get_product_text(products[product_index + change_num]),
                text=str(products[product_index + change_num]),
                reply_markup=product_keyboard
            )
            product_index += change_num

        await query.answer()


@dp.message_handler(state='*', commands=['compare_keywords'])
async def compare_keywords_start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.WAITING_KEYWORDS[0])
    await message.answer(messages.COMPARE_KEYWORD_START_MESSAGE)


@dp.message_handler(state=States.WAITING_KEYWORDS)
async def compare_keywords_get_keywords(message: types.Message):
    products = choose_gifts(message.text)
    # products = get_products()
    await show_product(message.from_user.id, products)
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()


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


def get_answers_by_query(callback_query: CallbackQuery):
    for i in callback_query.message.reply_markup:
        return [j[0]['text'] for j in i[1]]


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(messages.START_MESSAGE)


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply(messages.HELP_MESSAGE)


@dp.callback_query_handler(Text(startswith='ans_'))
async def callback_ans(query: CallbackQuery):
    ans_index = int(query.data.split('_')[1])
    # await query.message.edit_reply_markup(None)
    await bot.send_message(query.from_user.id, str(ans_index))
    await query.answer()


@dp.callback_query_handler(Text(startswith='multians_'))
async def callback_multians(query: CallbackQuery):
    action = query.data.split('_')[1]
    answers_list = get_answers_by_query(query)[:-1]
    if action == 'confirm':
        selected_indexes = []
        for index, answer in enumerate(answers_list):
            if check_mark_emoji in answer:
                selected_indexes.append(index)
        # await query.message.edit_reply_markup(None)
        await bot.send_message(query.from_user.id, str(selected_indexes))
        await query.answer()
        return

    ans_index = int(action)
    if check_mark_emoji not in answers_list[ans_index]:
        answers_list[ans_index] += ' ' + check_mark_emoji
    else:
        answers_list[ans_index] = answers_list[ans_index].replace(' ' + check_mark_emoji, '')
    await query.message.edit_reply_markup(get_keyboard(answers_list, is_multians=True))
    await query.answer()


@dp.message_handler(commands=['q1'])
async def question1(message: types.Message):
    question_text = 'Question text'
    answers_list = ['ans1', 'ans2', 'ans3', 'ans4', 'ans5', 'ans6']
    await message.answer(question_text, reply_markup=get_keyboard(answers_list))


@dp.message_handler(commands=['q2'])
async def question2(message: types.Message):
    question_text = 'Question text'
    answers_list = ['ans1', 'ans2', 'ans3', 'ans4', 'ans5', 'ans6']
    await message.answer(question_text, reply_markup=get_keyboard(answers_list, is_multians=True))


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


def get_products():
    return [
        {'asin': 'B08RQQFQKL',
         'avg_rating': 4.2,
         'cost': 4999,
         'description': 'About this item    CONVERTIBLE 2-IN-1 DESIGN: This flip-open '
                        'chair converts to a lounger/sleeper| Ideal for reading, '
                        'relaxing, playing or sleeping, your child will enjoy this '
                        'couch with siblings/friends | Recommended for ages 18 months+ '
                        '| Fits 1 to 2 small children    COMFY FOAM CONSTRUCTION: '
                        'Supportive foam keeps its shape and provides all-day comfort '
                        '| Soft and durable slipcover features side pocket to keep '
                        'books/tablet within reach | Lightweight chair is portable, '
                        'great for bedrooms, playrooms, gaming or studying    '
                        'STAIN-RESISTANT: Keep chair looking new with the built-in '
                        'Scotchgard stain release finish that helps most stains wash '
                        'out during normal laundering | Chair features a '
                        'machine-washable slipcover that zips off    CHILD-SAFE '
                        'ZIPPER: To prevent kids from opening the chair, we use a '
                        'childproof safety zipper that comes without a pull, it can '
                        'only be opened using a paperclip | Chair meets or exceeds '
                        'government and ASTM safety standards    EASY TO UNBOX: Ships '
                        'in a super-small box | Assembly required | Once unboxed chair '
                        'expands 5x (may take 24 hours to fully expand) | Chair: '
                        '23.5”W x 16.5”D x 15”H| Lounger Flipped Open: 23.5”W x 40.5”D '
                        'x 15”H    \n'
                        '› See more product details',
         'link': 'https://amazon.com/dp/B08RQQFQKL',
         'name': '1 Batman Cozee Flip-Out Chair - 2-in-1 Convertible Chair to Lounger '
                 'for Kids by Delta Children',
         'reviews_count': 2},
        {'asin': 'B08RQQFQKL',
         'avg_rating': 4.2,
         'cost': 4999,
         'description': 'About this item    CONVERTIBLE 2-IN-1 DESIGN: This flip-open '
                        'chair converts to a lounger/sleeper| Ideal for reading, '
                        'relaxing, playing or sleeping, your child will enjoy this '
                        'couch with siblings/friends | Recommended for ages 18 months+ '
                        '| Fits 1 to 2 small children    COMFY FOAM CONSTRUCTION: '
                        'Supportive foam keeps its shape and provides all-day comfort '
                        '| Soft and durable slipcover features side pocket to keep '
                        'books/tablet within reach | Lightweight chair is portable, '
                        'great for bedrooms, playrooms, gaming or studying    '
                        'STAIN-RESISTANT: Keep chair looking new with the built-in '
                        'Scotchgard stain release finish that helps most stains wash '
                        'out during normal laundering | Chair features a '
                        'machine-washable slipcover that zips off    CHILD-SAFE '
                        'ZIPPER: To prevent kids from opening the chair, we use a '
                        'childproof safety zipper that comes without a pull, it can '
                        'only be opened using a paperclip | Chair meets or exceeds '
                        'government and ASTM safety standards    EASY TO UNBOX: Ships '
                        'in a super-small box | Assembly required | Once unboxed chair '
                        'expands 5x (may take 24 hours to fully expand) | Chair: '
                        '23.5”W x 16.5”D x 15”H| Lounger Flipped Open: 23.5”W x 40.5”D '
                        'x 15”H    \n'
                        '› See more product details',
         'link': 'https://amazon.com/dp/B08RQQFQKL',
         'name': '2 Batman Cozee Flip-Out Chair - 2-in-1 Convertible Chair to Lounger '
                 'for Kids by Delta Children',
         'reviews_count': 2},
        {'asin': 'B08RQQFQKL',
         'avg_rating': 4.2,
         'cost': 4999,
         'description': 'About this item    CONVERTIBLE 2-IN-1 DESIGN: This flip-open '
                        'chair converts to a lounger/sleeper| Ideal for reading, '
                        'relaxing, playing or sleeping, your child will enjoy this '
                        'couch with siblings/friends | Recommended for ages 18 months+ '
                        '| Fits 1 to 2 small children    COMFY FOAM CONSTRUCTION: '
                        'Supportive foam keeps its shape and provides all-day comfort '
                        '| Soft and durable slipcover features side pocket to keep '
                        'books/tablet within reach | Lightweight chair is portable, '
                        'great for bedrooms, playrooms, gaming or studying    '
                        'STAIN-RESISTANT: Keep chair looking new with the built-in '
                        'Scotchgard stain release finish that helps most stains wash '
                        'out during normal laundering | Chair features a '
                        'machine-washable slipcover that zips off    CHILD-SAFE '
                        'ZIPPER: To prevent kids from opening the chair, we use a '
                        'childproof safety zipper that comes without a pull, it can '
                        'only be opened using a paperclip | Chair meets or exceeds '
                        'government and ASTM safety standards    EASY TO UNBOX: Ships '
                        'in a super-small box | Assembly required | Once unboxed chair '
                        'expands 5x (may take 24 hours to fully expand) | Chair: '
                        '23.5”W x 16.5”D x 15”H| Lounger Flipped Open: 23.5”W x 40.5”D '
                        'x 15”H    \n'
                        '› See more product details',
         'link': 'https://amazon.com/dp/B08RQQFQKL',
         'name': '3 Batman Cozee Flip-Out Chair - 2-in-1 Convertible Chair to Lounger '
                 'for Kids by Delta Children',
         'reviews_count': 2},
        {'asin': 'B08RQQFQKL',
         'avg_rating': 4.2,
         'cost': 4999,
         'description': 'About this item    CONVERTIBLE 2-IN-1 DESIGN: This flip-open '
                        'chair converts to a lounger/sleeper| Ideal for reading, '
                        'relaxing, playing or sleeping, your child will enjoy this '
                        'couch with siblings/friends | Recommended for ages 18 months+ '
                        '| Fits 1 to 2 small children    COMFY FOAM CONSTRUCTION: '
                        'Supportive foam keeps its shape and provides all-day comfort '
                        '| Soft and durable slipcover features side pocket to keep '
                        'books/tablet within reach | Lightweight chair is portable, '
                        'great for bedrooms, playrooms, gaming or studying    '
                        'STAIN-RESISTANT: Keep chair looking new with the built-in '
                        'Scotchgard stain release finish that helps most stains wash '
                        'out during normal laundering | Chair features a '
                        'machine-washable slipcover that zips off    CHILD-SAFE '
                        'ZIPPER: To prevent kids from opening the chair, we use a '
                        'childproof safety zipper that comes without a pull, it can '
                        'only be opened using a paperclip | Chair meets or exceeds '
                        'government and ASTM safety standards    EASY TO UNBOX: Ships '
                        'in a super-small box | Assembly required | Once unboxed chair '
                        'expands 5x (may take 24 hours to fully expand) | Chair: '
                        '23.5”W x 16.5”D x 15”H| Lounger Flipped Open: 23.5”W x 40.5”D '
                        'x 15”H    \n'
                        '› See more product details',
         'link': 'https://amazon.com/dp/B08RQQFQKL',
         'name': '4 Batman Cozee Flip-Out Chair - 2-in-1 Convertible Chair to Lounger '
                 'for Kids by Delta Children',
         'reviews_count': 2}
    ]


executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
