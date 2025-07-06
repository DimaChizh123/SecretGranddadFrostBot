from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from app.db.rooms import check_room, get_room_name_code
from app.keyboards import KeyboardFactory as KB
from app.utils.helpers import get_user

router = Router()

class User(StatesGroup):
    code = State()
    username = State()

@router.message(F.text == "Вступить в комнату")
async def join_room(message: Message, state: FSMContext):
    await state.set_state(User.code)
    await message.answer("Введи код комнаты")

@router.message(User.code)
async def set_id(message: Message, state: FSMContext):
    try:
        code = int(message.text.strip())
    except ValueError:
        await message.answer("К сожалению, такая комната не найдена")
        await state.clear()
        return
    await state.update_data(code=code)
    if await check_room(code):
        await state.set_state(User.username)
        await message.answer(f"Добавляем в комнату: {await get_room_name_code(code)}\nВведи своё имя", reply_markup=KB.use_tg_name)
    else:
        await message.answer("К сожалению, такая комната не найдена")
        await state.clear()

@router.message(User.username)
async def set_username(message: Message, state: FSMContext):
    if not await state.get_value("username"):
        await state.update_data(username=message.text.strip())
    await get_user(message, state, message.from_user.id)
