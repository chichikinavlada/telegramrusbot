"""Кнопки, которые бот показывает под сообщениями."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    """Главное меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Разобрать текст', callback_data='menu:analyze')],
        [
            InlineKeyboardButton(text='История', callback_data='menu:history'),
            InlineKeyboardButton(text='Статистика', callback_data='menu:stats'),
        ],
        [InlineKeyboardButton(text='Что умеет бот', callback_data='menu:help')],
    ])


def back_button() -> InlineKeyboardMarkup:
    """Одна кнопка для возврата в меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад в меню', callback_data='menu:home')],
    ])


def after_analysis_buttons() -> InlineKeyboardMarkup:
    """Кнопки после анализа текста."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Разобрать еще текст', callback_data='menu:analyze')],
        [InlineKeyboardButton(text='Назад в меню', callback_data='menu:home')],
    ])


def after_section_buttons() -> InlineKeyboardMarkup:
    """Кнопки после просмотра истории или статистики."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Разобрать текст', callback_data='menu:analyze')],
        [InlineKeyboardButton(text='Назад в меню', callback_data='menu:home')],
    ])
