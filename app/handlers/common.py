from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.db.rooms import get_room_name_code, check_room
from app.db.users import get_rooms, show_room
from app.keyboards import KeyboardFactory as KB
from app.handlers.join_room import User
from app.utils.callback_parser import parse_callback_data
from app.utils.helpers import get_user, get_room

router = Router()

@router.message(CommandStart())
async def start(message: Message, command: CommandObject, state: FSMContext):
    if command.args:
        try:
            payload = int(command.args)
        except ValueError:
            await message.answer(f'Некорректная ссылка!')
            return
        await message.answer(f'Злооо!\nДанный бот реализует игру "Тайный Санта"')
        if check_room(payload):
            await message.answer(f'Сейчас присоединим тебя в комнату: {await get_room_name_code(payload)}\nВведи своё имя', reply_markup=KB.use_tg_name)
            await state.update_data(code=payload)
            await state.set_state(User.username)
        else:
            await message.answer("Ошибка! Не найдено")
    else:
        await message.answer(f'Доброоо!\nДанный бот реализует игру "Тайный Санта"', reply_markup=KB.room_manager)

@router.message(F.text == "Управление комнатами")
async def manage_rooms(message: Message):
    await message.answer("Выбери нужную комнату", reply_markup=await KB.room_list(await get_rooms(message.from_user.id)))

@router.callback_query(F.data.startswith("view:guest:"))
async def guest_room(call: CallbackQuery):
    data = parse_callback_data(call.data)
    room = data.id
    message, code = await show_room(room, call.from_user.id, call.bot)
    await call.answer()
    await call.message.answer(message)

@router.callback_query(F.data == "tg_name")
async def tg_name(call: CallbackQuery, state: FSMContext):
    await state.update_data(username=f'{call.from_user.first_name or ""} {call.from_user.last_name or ""}')
    await call.answer()
    if await state.get_value("name"):
        await get_room(call.message, state, call.from_user.id)
    else:
        await get_user(call.message, state, call.from_user.id)