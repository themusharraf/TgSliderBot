import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv
from aiogram.filters.command import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Welcome! Use /send to receive the image with inline buttons.")


@dp.message(Command('send'))
async def send_image(message: types.Message):
    # Create caption
    caption = (
        "0. YouTube is an American online video sharing and social media platform headquartered in "
        "San Bruno, California. It was launched on February 14, 2005, by Steve Chen, Chad Hurley, and Jawed Karim."
    )

    buttons = [
        [
            InlineKeyboardButton(text="«", callback_data='previous'),
            InlineKeyboardButton(text="»", callback_data='next')
        ],
        [InlineKeyboardButton(text="Select", callback_data='select'), ]
    ]
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    # Send photo with caption and inline keyboard
    await bot.send_photo(chat_id=message.chat.id, photo='https://images.app.goo.gl/vnoA5ZCwRdZ35xKg9', caption=caption,
                         reply_markup=keyboard)


@dp.callback_query(lambda c: c.data)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    if data == 'previous':
        await bot.answer_callback_query(callback_query.id, text='Previous button pressed.')
    elif data == 'select':
        await bot.answer_callback_query(callback_query.id, text='Select button pressed.')
    elif data == 'next':
        await bot.answer_callback_query(callback_query.id, text='Next button pressed.')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
