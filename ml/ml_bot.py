import os

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ml.utils import get_next, save_answer
from filters import get_numbers

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    rent = State()


async def next_message(chat_id):
    item = get_next()

    if item:
        key = "answer:{message}:{tag_id}".format(
            message=item.meta["raw_id"],
            tag_id=item.tag.id,
        )
        buttons = []
        markup = None

        if item.tag.type is bool:
            button_yes = InlineKeyboardButton(f"{item.tag.name} ✅", callback_data=f"{key}:1")
            button_no = InlineKeyboardButton("❌", callback_data=f"{key}:0")
            markup = InlineKeyboardMarkup().row(button_yes, button_no)
        elif item.tag.type is int:
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            for number in get_numbers(item.meta["data"]):
                if len(str(number)) < 2:
                    continue
                markup.add(InlineKeyboardButton(f"{number}", callback_data=f"{key}:{number}"))
            if len(markup.inline_keyboard) < 5:
                markup.add(InlineKeyboardButton("no price", callback_data=f"{key}:null"))

        await bot.send_message(chat_id, item.meta["data"], reply_markup=markup)
    else:
        await bot.send_message(chat_id, "У меня нет больше заданий, приходи позже")


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await Form.rent.set()
    await next_message(message.chat.id)


@dp.callback_query_handler(lambda callback_query: True, state="*")
async def some_callback_handler(callback_query: types.CallbackQuery):
    _, raw_id, tag_id, answer = callback_query.data.split(":")
    save_answer(raw_id, tag_id, answer)

    await next_message(callback_query.message.chat.id)


@dp.message_handler(state="*", commands="cancel")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply("Возвращайся скорей!!!", reply_markup=types.ReplyKeyboardRemove())

if __name__ == "__main__":
    executor.start_polling(dp)
