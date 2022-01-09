import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.builtin import Text

import users_db_functions
import bot_data
from compare_keywords import choose_gifts
from states import States
from config import get_token_from_dotenv
import keyboards
from consts import Commands, Messages, Emojis

logging.basicConfig(level=logging.INFO)

bot = Bot(token=get_token_from_dotenv())
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())


async def set_default_commands():
    await dp.bot.set_my_commands([
        types.BotCommand('start', Commands.START_COMMAND),
        types.BotCommand('help', Commands.HELP_COMMAND),
        types.BotCommand('compare_keywords', Commands.KEYWORDS_ALGORITHM_COMMAND),
        types.BotCommand('tree_algorithm', Commands.TREE_ALGORITHM_COMMAND),
        types.BotCommand('bayes', Commands.BAYES_ALGORITHM_COMMAND),
        types.BotCommand('liked', Commands.LIKED_COMMAND)
    ])


def get_product_text(product: dict):
    print(product)
    name = product['name']
    link = product['link']
    return name + '\n' + link


async def show_products(user_id, products: list):
    product_index = 0
    if len(products) == 0:
        await bot.send_message(user_id, Messages.LIKED_EMPTY_MESSAGE)
        return
    product = products[product_index]
    await bot.send_message(
        user_id, get_product_text(product),
        reply_markup=await keyboards.get_product_keyboard(user_id, products[product_index])
    )

    @dp.callback_query_handler(Text(startswith='product_'))
    async def product_actions_handler(query: CallbackQuery):
        nonlocal product_index
        action = query.data.split('_')[1]
        if action == 'like':
            users_db_functions.add_to_favourite(user_id=user_id, product_id=int(product['id']))
            await query.message.edit_reply_markup(reply_markup=await keyboards.get_product_keyboard(user_id, product))
            await query.answer()
            return
        elif action == 'unlike':
            users_db_functions.remove_from_favourite(user_id=user_id, product_id=int(product['id']))
            if len(products) == 0:
                await bot.send_message(user_id, Messages.LIKED_EMPTY_MESSAGE)
                await query.answer()
                return
            await query.message.edit_reply_markup(reply_markup=await keyboards.get_product_keyboard(user_id, product))
            await query.answer()
            return
        change_num = 1 if action == 'next' else -1
        if 0 <= product_index + change_num < len(products):
            product_index += change_num
            await query.message.edit_text(
                text=get_product_text(product),
                reply_markup=await keyboards.get_product_keyboard(user_id, product)
            )
        await query.answer()


@dp.message_handler(commands=['compare_keywords'])
async def compare_keywords_start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.WAITING_KEYWORDS[0])
    await message.answer(Messages.START_KEYWORDS_ALGORITHM_MESSAGE)


@dp.message_handler(state=States.WAITING_KEYWORDS)
async def compare_keywords_get_keywords(message: types.Message):
    products = choose_gifts(message.text)
    await show_products(message.from_user.id, products)
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()


def get_answers_by_query(callback_query: CallbackQuery):
    for i in callback_query.message.reply_markup:
        return [j[0]['text'] for j in i[1]]


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply(Messages.START_MESSAGE)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await set_default_commands()
    await message.reply(Messages.HELP_MESSAGE)


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
    await query.message.answer(text=question_text, reply_markup=keyboards.get_scale_keyboard())
    await query.answer()


@dp.callback_query_handler(Text(startswith='multians_'))
async def callback_multians(query: CallbackQuery):
    action = query.data.split('_')[1]
    answers_list = get_answers_by_query(query)[:-1]
    if action == 'confirm':
        selected_answers = []
        for answer in answers_list:
            if Emojis.CHECK_MARK_EMOJI in answer:
                selected_answers.append(answer.replace(' ' + Emojis.CHECK_MARK_EMOJI, ''))
        tree_session = bot_data.get_tree_session(query.from_user.id)
        products = tree_session.new_answer(selected_answers)
        if len(products) > 0:
            await show_products(query.from_user.id, products)
            await query.answer()
            return
        question = tree_session.get_question()
        print(question)
        await query.message.answer(Messages.SELECT_KEYWORDS_MESSAGE, reply_markup=keyboards.get_keyboard(question, is_multians=True))
        await query.answer()
        return

    ans_index = int(action)
    if Emojis.CHECK_MARK_EMOJI not in answers_list[ans_index]:
        answers_list[ans_index] += ' ' + Emojis.CHECK_MARK_EMOJI
    else:
        answers_list[ans_index] = answers_list[ans_index].replace(' ' + Emojis.CHECK_MARK_EMOJI, '')
    await query.message.edit_reply_markup(keyboards.get_keyboard(answers_list, is_multians=True))
    await query.answer()


@dp.message_handler(commands=['tree_algorithm'])
async def tree_algorithm_start(message: types.Message):
    tree_session = bot_data.get_tree_session(message.from_user.id)
    question = tree_session.get_question()
    await message.answer(Messages.START_TREE_ALGORITHM)
    await message.answer(Messages.SELECT_KEYWORDS_MESSAGE, reply_markup=keyboards.get_keyboard(question, is_multians=True))


@dp.message_handler(commands=['bayes'])
async def bayes_algorithm_start(message: types.Message):
    bayes_session = bot_data.get_bayes_session(message.from_user.id)
    question = bayes_session.get_question()
    await message.answer(Messages.START_BAYES_ALGORITHM)
    question_text = question[0]
    await message.answer(text=question_text, reply_markup=keyboards.get_scale_keyboard())


@dp.message_handler(commands=['liked'])
async def get_liked(message: types.Message):
    user_id = message.from_user.id
    products = users_db_functions.get_users_favourite(user_id=user_id)
    await show_products(user_id=user_id, products=products)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
