from typing import ClassVar

from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.users import get_users_list
from app.utils.callback_parser import make_callback_data

class KeyboardFactory:

    room_manager: ClassVar[ReplyKeyboardMarkup] = ReplyKeyboardMarkup(
        keyboard=[
        [KeyboardButton(text="Создать комнату"), KeyboardButton(text="Вступить в комнату")],
        [KeyboardButton(text="Управление комнатами")]
    ],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выбери действие"
    )

    use_tg_name: ClassVar[ReplyKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Оставить имя в Telegram", callback_data="tg_name")]
        ]
    )

    @staticmethod
    def controller(room_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Исключить участника", callback_data=make_callback_data("select",  room_id)),
         InlineKeyboardButton(text="Удалить комнату", callback_data=make_callback_data("delete", room_id))
        ],
        [InlineKeyboardButton(text="Запустить", callback_data=make_callback_data("run", room_id))]
    ])

    @staticmethod
    async def room_list(rooms: list[list[tuple[int, str]]]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        admin_rooms, guest_rooms = rooms
        for room_id, name in admin_rooms:
            builder.add(InlineKeyboardButton(text=f"⭐️ {name}", callback_data=make_callback_data("view_admin", room_id)))
        for room_id, name in guest_rooms:
            builder.add(InlineKeyboardButton(text=name, callback_data=make_callback_data("view_guest", room_id)))
        return builder.adjust(2).as_markup()

    @staticmethod
    async def users_list(bot: Bot, room_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        users = (await get_users_list(bot, room_id))[1:]
        for user in users:
            builder.add(InlineKeyboardButton(text=user[1], callback_data=make_callback_data("remove", user[0], room_id)))
        return builder.adjust(1).as_markup()

    @staticmethod
    async def quit(user_id: int, room_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Выйти из комнаты", callback_data=make_callback_data("remove", user_id, room_id))]
        ])