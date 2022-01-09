import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.builtin import Text
from pprint import pprint

import users_db_functions
import bot_data
from compare_keywords import choose_gifts
from states import States
from config import get_token_from_dotenv

logging.basicConfig(level=logging.INFO)

bot = Bot(token=get_token_from_dotenv())
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())

check_mark_emoji = '✅'


async def set_default_commands():
    await dp.bot.set_my_commands([
        types.BotCommand('start', 'Start bot'),
        types.BotCommand('help', 'Get Help'),
        types.BotCommand('compare_keywords', 'Compare keywords algorithm'),
        types.BotCommand('tree_algorithm', 'Tree algorithm'),
        types.BotCommand('liked', 'Your liked products'),
        types.BotCommand('bayes', 'Bayes Algorithm')
    ])


def get_product_text(product: dict):
    print(product)
    name = product['name']
    link = product['link']
    return name + '\n' + link


async def get_product_keyboard(user_id: int, product: dict):
    product_keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text='Previous', callback_data='product_previous'),
        InlineKeyboardButton(text='Next', callback_data='product_next'),
    )
    if product not in users_db_functions.get_users_favourite(user_id=user_id):
        product_keyboard.add(InlineKeyboardButton(text='Add to liked', callback_data='product_like'))
    else:
        product_keyboard.add(InlineKeyboardButton(text='Remove form liked', callback_data='product_unlike'))
    return product_keyboard


async def show_products(user_id, products: list):
    product_index = 0

    if len(products) == 0:
        await bot.send_message(user_id, 'Your liked products is empty')
        return

    product = products[product_index]

    await bot.send_message(
        user_id, get_product_text(product),
        reply_markup=await get_product_keyboard(user_id, products[product_index])
    )

    @dp.callback_query_handler(Text(startswith='product_'))
    async def product_actions_handler(query: CallbackQuery):
        nonlocal product_index
        action = query.data.split('_')[1]
        if action == 'like':
            users_db_functions.add_to_favourite(user_id=user_id, product_id=int(product['id']))
            await query.message.edit_reply_markup(reply_markup=await get_product_keyboard(user_id, product))
            await query.answer()
            return
        elif action == 'unlike':
            users_db_functions.remove_from_favourite(user_id=user_id, product_id=int(product['id']))
            if len(products) == 0:
                await bot.send_message(user_id, 'Your liked products is empty')
                await query.answer()
                return
            await query.message.edit_reply_markup(reply_markup=await get_product_keyboard(user_id, product))
            await query.answer()
            return
        change_num = 1 if action == 'next' else -1
        if 0 <= product_index + change_num < len(products):
            product_index += change_num
            await query.message.edit_text(
                text=get_product_text(product),
                reply_markup=await get_product_keyboard(user_id, product)
            )
        await query.answer()


@dp.message_handler(commands=['compare_keywords'])
async def compare_keywords_start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.WAITING_KEYWORDS[0])
    await message.answer('Start "Compare Keywords" algorithm...')


@dp.message_handler(state=States.WAITING_KEYWORDS)
async def compare_keywords_get_keywords(message: types.Message):
    products = choose_gifts(message.text)
    # products = get_products()
    await show_products(message.from_user.id, products)
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


def get_scale_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Yes', callback_data='scale_1'),
        InlineKeyboardButton(text='Dont know', callback_data='scale_0.5'),
        InlineKeyboardButton(text='No', callback_data='scale_0')
    )


def get_answers_by_query(callback_query: CallbackQuery):
    for i in callback_query.message.reply_markup:
        return [j[0]['text'] for j in i[1]]


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply('start message...')


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await set_default_commands()
    await message.reply('help message...')


@dp.callback_query_handler(Text(startswith='scale_'))
async def callback_scale_ans(query: CallbackQuery):
    ans_coefficient = float(query.data.split('_')[1])
    bayes_session = bot_data.get_bayes_session(query.from_user.id)
    bayes_session.new_answer(ans_coefficient)
    question = bayes_session.get_question()
    if question is None:
        products = bayes_session.get_presents()
        print(products)
    question_text = question[0]
    await query.message.answer(text=question_text, reply_markup=get_scale_keyboard())
    await query.answer()


@dp.callback_query_handler(Text(startswith='multians_'))
async def callback_multians(query: CallbackQuery):
    action = query.data.split('_')[1]
    answers_list = get_answers_by_query(query)[:-1]
    if action == 'confirm':
        selected_answers = []
        for answer in answers_list:
            if check_mark_emoji in answer:
                selected_answers.append(answer.replace(' ' + check_mark_emoji, ''))
        tree_session = bot_data.get_tree_session(query.from_user.id)
        products = tree_session.new_answer(selected_answers)
        if len(products) > 0:
            await show_products(query.from_user.id, products)
            await query.answer()
            return
        question = tree_session.get_question()
        print(question)
        await query.message.answer('Select Keyword', reply_markup=get_keyboard(question, is_multians=True))
        await query.answer()
        return

    ans_index = int(action)
    if check_mark_emoji not in answers_list[ans_index]:
        answers_list[ans_index] += ' ' + check_mark_emoji
    else:
        answers_list[ans_index] = answers_list[ans_index].replace(' ' + check_mark_emoji, '')
    await query.message.edit_reply_markup(get_keyboard(answers_list, is_multians=True))
    await query.answer()


@dp.message_handler(commands=['tree_algorithm'])
async def tree_algorithm_start(message: types.Message):
    tree_session = bot_data.get_tree_session(message.from_user.id)
    question = tree_session.get_question()
    await message.answer('Start "Tree" algorithm')
    await message.answer('Select Keyword', reply_markup=get_keyboard(question, is_multians=True))


@dp.message_handler(commands=['bayes'])
async def bayes_algorithm_start(message: types.Message):
    bayes_session = bot_data.get_bayes_session(message.from_user.id)
    question = bayes_session.get_question()
    await message.answer('Start "Bayes" algorithm')
    question_text = question[0]
    await message.answer(text=question_text, reply_markup=get_scale_keyboard())


@dp.message_handler(commands=['liked'])
async def get_liked(message: types.Message):
    user_id = message.from_user.id
    products = users_db_functions.get_users_favourite(user_id=user_id)
    await show_products(user_id=user_id, products=products)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
