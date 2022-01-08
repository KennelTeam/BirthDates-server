import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

TOKEN = '5052322493:AAHOqvNEnY-TbhuATpxSTV7sX5InTwWx4Bc'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

check_mark_emoji = '✅'


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


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Welcome message")


@dp.callback_query_handler(lambda m: m.data.startswith('ans_'))
async def callback_ans(query: CallbackQuery):
    ans_index = int(query.data.split('_')[1])
    # await query.message.edit_reply_markup(None)
    await bot.send_message(query.from_user.id, str(ans_index))
    await query.answer()


@dp.callback_query_handler(lambda m: m.data.startswith('multians_'))
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


executor.start_polling(dp, skip_updates=True)
