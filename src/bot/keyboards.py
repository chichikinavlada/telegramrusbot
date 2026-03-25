from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def glavnoe_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Разобрать текст", callback_data="menu:analiz")],
            [
                InlineKeyboardButton(text="История", callback_data="menu:history"),
                InlineKeyboardButton(text="Статистика", callback_data="menu:stats"),
            ],
            [InlineKeyboardButton(text="Что умеет бот", callback_data="menu:help")],
        ]
    )


def knopka_nazad() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад в меню", callback_data="menu:home")]]
    )


def knopki_posle_analiza() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Разобрать еще текст", callback_data="menu:analiz")],
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu:home")],
        ]
    )


def knopki_posle_razdela() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Разобрать текст", callback_data="menu:analiz")],
            [InlineKeyboardButton(text="Назад в меню", callback_data="menu:home")],
        ]
    )
