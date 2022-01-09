import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.builtin import Text

from consts import Messages
from consts import Commands
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
            product_index += change_num
            await query.message.edit_text(
                # text=get_product_text(products[product_index + change_num]),
                text=str(products[product_index]),
                reply_markup=product_keyboard
            )

        await query.answer()


@dp.message_handler(state='*', commands=['compare_keywords'])
async def compare_keywords_start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.WAITING_KEYWORDS[0])
    await message.answer(Messages.COMPARE_KEYWORD_START_MESSAGE)


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
    await message.reply(Messages.START_MESSAGE)


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply(Messages.HELP_MESSAGE)


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


executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
