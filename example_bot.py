from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters.callback_data import CallbackQuery
from aiogram.filters import Command
from datepicker import DatePicker, DpCallback
import logging
from datetime import datetime, timedelta
from config import Config


API_TOKEN = Config.API_KEY

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

datepicker = DatePicker()


@dp.message(Command(commands=['start']))    # start command
async def start(message: Message):
    


    await message.answer(
        'Select date:',
        reply_markup=await datepicker.start_calendar()
    )


@dp.callback_query(DpCallback.filter())
async def process_dialog_calendar(
    callback: CallbackQuery, callback_data: DpCallback
):
    date = await datepicker.process_selection(callback, callback_data)
    if date:
        await callback.message.edit_text(f"Selected date {date} ✅")



if __name__ == '__main__':
    try:
        dp.run_polling(bot)
    finally:
        bot.session.close()
        print('Bot stopped.')