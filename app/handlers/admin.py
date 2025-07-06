from aiogram import Router, F
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import CallbackQuery

from app.db.rooms import delete_room_from_db, get_room_name_id
from app.db.users import show_room, remove_user_from_db, get_users_list, shuffle_names
from app.utils.callback_parser import parse_callback_data

from app.keyboards import KeyboardFactory as KB

router = Router()

@router.callback_query(F.data.startswith("view:admin:"))
async def admin_room(call: CallbackQuery):
    data = parse_callback_data(call.data)
    room = data.id
    message, code = await show_room(room, call.from_user.id, call.bot)
    if code:
        await call.message.answer(message, reply_markup=KB.controller(room))
    else:
        await call.message.answer(message)

@router.callback_query(F.data.startswith("select:user:"))
async def remove_user(call: CallbackQuery):
    data = parse_callback_data(call.data)
    user = data.id
    await call.message.answer("Выберите участника", reply_markup=await KB.users_list(user))

@router.callback_query(F.data.startswith("remove:user:"))
async def user_removed(call: CallbackQuery):
    data = parse_callback_data(call.data)
    user = data.id
    await remove_user_from_db(user)
    await call.message.answer("Пользователь исключён из комнаты!")

@router.callback_query(F.data.startswith("delete:room:"))
async def delete_room(call: CallbackQuery):
    data = parse_callback_data(call.data)
    room = data.id
    await delete_room_from_db(room)
    await call.message.answer("Комната успешно удалена!")

@router.callback_query(F.data.startswith("run:room:"))
async def run_room(call: CallbackQuery):
    data = parse_callback_data(call.data)
    room = data.id
    users_list = await get_users_list(room)
    if not users_list:
        await call.message.answer("Не удалось запустить! Возможно, комната удалена")
        return
    if len(users_list) < 2:
        await call.message.answer("Для участия в игре нужно как минимум 2 человека!")
        return
    ids = []
    names = []
    for user in users_list:
        ids.append(user[0])
        names.append(user[1])
    names = await shuffle_names(names)
    room_name = (await get_room_name_id(room))[0]
    my_bot = call.bot
    for i in range(len(names)):
        try:
            await my_bot.send_message(chat_id=ids[i], text=f"Комната {room_name}:\nТы даришь подарок {names[i]}")
        except TelegramForbiddenError:
            await my_bot.send_message(chat_id=ids[0], text=f"Комната {room_name}:\nПользователь {ids[i]} заблокировал бота, не удалось отправить ему сообщение")


