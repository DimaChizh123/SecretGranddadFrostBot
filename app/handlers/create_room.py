from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from app.keyboards import KeyboardFactory as KB
from app.utils.getters import get_room

router = Router()

class Room(StatesGroup):
    name = State()
    username = State()

@router.message(F.text == "Создать комнату")
async def create_room(message: Message, state: FSMContext):
    await state.set_state(Room.name)
    await message.answer("Введи название своей комнаты")

@router.message(Room.name)
async def name_room(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(Room.username)
    await message.answer("Введи своё имя", reply_markup=KB.use_tg_name)

@router.message(Room.username)
async def set_name(message: Message, state: FSMContext):
    if not await state.get_value("username"):
        await state.update_data(username=message.text.strip())
    await get_room(message, state, message.from_user.id)