import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

from data import slides

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")


class Form(StatesGroup):
    viewing = State()
    finish = State()


bot = Bot(token=TOKEN)
dp = Dispatcher()


# Function to generate slider buttons
def generate_slider_buttons(current_index: int):
    builder = InlineKeyboardBuilder()
    if current_index > 0:
        builder.button(text="Previous", callback_data=f"prev_{current_index}")
    if current_index < len(slides) - 1:
        builder.button(text="Next", callback_data=f"next_{current_index}")
    builder.button(text="Select", callback_data=f"select_{current_index}")
    builder.button(text="Cancel", callback_data="cancel")
    return builder.as_markup()


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.viewing)
    await state.update_data(current_index=0)
    current_slide = slides[0]
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=current_slide["photo"],
        caption=current_slide["text"],
        parse_mode="MarkdownV2",
        reply_markup=generate_slider_buttons(0)
    )


@dp.callback_query(lambda c: c.data and c.data.startswith("prev_"))
async def callback_prev(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("current_index", 0)
    current_index = max(current_index - 1, 0)
    await state.update_data(current_index=current_index)
    current_slide = slides[current_index]
    await callback_query.message.edit_media(
        types.InputMediaPhoto(
            media=current_slide["photo"],
            caption=current_slide["text"],
            parse_mode="MarkdownV2"
        ),
        reply_markup=generate_slider_buttons(current_index)
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data and c.data.startswith("next_"))
async def callback_next(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_index = data.get("current_index", 0)
    current_index = min(current_index + 1, len(slides) - 1)
    await state.update_data(current_index=current_index)
    current_slide = slides[current_index]
    await callback_query.message.edit_media(
        types.InputMediaPhoto(
            media=current_slide["photo"],
            caption=current_slide["text"],
            parse_mode="MarkdownV2"
        ),
        reply_markup=generate_slider_buttons(current_index)
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data and c.data.startswith("select_"))
async def callback_select(callback_query: types.CallbackQuery):
    selected_index = int(callback_query.data.split("_")[1])
    await bot.send_message(callback_query.from_user.id, f"Select {selected_index}")
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "cancel")
async def callback_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Cancel")
    await state.finish()
    await callback_query.answer(text="Completed")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
