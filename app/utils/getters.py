from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.deep_linking import create_start_link

from app.db.rooms import generate_code, add_room
from app.db.users import add_user

async def get_room(message: Message, state: FSMContext, user):
    code = await generate_code()
    name = await state.get_value("name")
    username = await state.get_value("username")
    await add_room(code, name, user, username)
    await message.answer(f"Комната создана!\n{name} (код: {code})\nСсылка: {await create_start_link(message.bot, str(code))}")
    await state.clear()

async def get_user(message: Message, state: FSMContext, user):
    code = await state.get_value("code")
    username = await state.get_value("username")
    await message.answer(await add_user(code, user, username, message.bot))
    await state.clear()
