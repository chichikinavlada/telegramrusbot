"""Обработчики сообщений и кнопок бота."""

import os

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message

from src.bot.keyboards import after_analysis_buttons, after_section_buttons, back_button, main_menu
from src.services.analyzer import analyze_text
from src.services.charts import make_chart
from src.services.database import get_recent_analyses, get_user_stats, save_analysis

router = Router()

MIN_LENGTH = 30

HELP_TEXT = (
    'Я разбираю русский учебный текст.\n\n'
    'Могу посчитать слова и предложения, показать частотные леммы, '
    'найти людей, места и организации, построить график и сохранить результат в историю.\n\n'
    f'Нажми «Разобрать текст» и пришли фрагмент длиной хотя бы {MIN_LENGTH} символов. '
    'Длинные тексты Telegram режет на несколько сообщений, и я разберу каждое отдельно, '
    'поэтому лучше присылать до 4000 символов.'
)


def format_result(result: dict) -> str:
    """Собирает текст отчёта из результата анализа."""
    lemmas = []
    for lemma, count in result['top_lemmas']:
        lemmas.append(f'{lemma} ({count})')
    lemmas_text = ', '.join(lemmas)
    if lemmas_text == '':
        lemmas_text = 'нет данных'

    if len(result['entities']) == 0:
        entities_text = 'не найдены'
    else:
        parts = []
        for name, values in result['entities'].items():
            parts.append(f'{name}: ' + ', '.join(values[:5]))
        entities_text = '; '.join(parts)

    return (
        'Готово, вот что получилось.\n'
        f'Слов: {result["word_count"]}\n'
        f'Предложений: {result["sentence_count"]}\n'
        f'Частотные леммы: {lemmas_text}\n'
        f'Сущности: {entities_text}'
    )


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        'Привет! Это бот, который разбирает русский учебный текст. Выбери, что тебе нужно.',
        reply_markup=main_menu(),
    )


@router.callback_query(F.data == 'menu:home')
async def show_menu(callback: CallbackQuery):
    await callback.message.answer('Вот меню.', reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == 'menu:help')
async def show_help(callback: CallbackQuery):
    await callback.message.answer(HELP_TEXT, reply_markup=back_button())
    await callback.answer()


@router.callback_query(F.data == 'menu:analyze')
async def ask_for_text(callback: CallbackQuery):
    await callback.message.answer(
        'Пришли учебный текст одним сообщением, я его разберу.',
        reply_markup=back_button(),
    )
    await callback.answer()


@router.callback_query(F.data == 'menu:history')
async def show_history(callback: CallbackQuery):
    rows = get_recent_analyses(callback.from_user.id)
    if len(rows) == 0:
        text = 'История пока пустая. Сначала разбери хотя бы один текст.'
    else:
        text = 'Последние анализы:\n'
        number = 1
        for created_at, word_count, sentence_count, lemmas in rows:
            top3 = ', '.join(lemmas.split(', ')[:3])
            if top3 == '':
                top3 = 'нет'
            text += f'{number}) {created_at} (UTC) | слов: {word_count} | предложений: {sentence_count} | леммы: {top3}\n'
            number += 1
    await callback.message.answer(text, reply_markup=after_section_buttons())
    await callback.answer()


@router.callback_query(F.data == 'menu:stats')
async def show_stats(callback: CallbackQuery):
    total, average = get_user_stats(callback.from_user.id)
    text = f'Твоя статистика:\nАнализов всего: {total}\nСредний размер текста: {average} слов'
    await callback.message.answer(text, reply_markup=after_section_buttons())
    await callback.answer()


@router.message(F.text)
async def handle_text(message: Message):
    text = message.text.strip()

    # неизвестные команды
    if text.startswith('/'):
        await message.answer('Такой команды я не знаю, выбери действие в меню.', reply_markup=main_menu())
        return

    if len(text) < MIN_LENGTH:
        await message.answer(
            f'Текст слишком короткий, пришли хотя бы {MIN_LENGTH} символов.',
            reply_markup=back_button(),
        )
        return

    wait_message = await message.answer('Секунду, смотрю текст...')

    try:
        result = analyze_text(text)
    except Exception:
        await wait_message.edit_text('Не получилось разобрать этот текст. Попробуй прислать другой.')
        return

    save_analysis(message.from_user.id, result)
    await wait_message.delete()

    # если лемм нет (например, в тексте одни цифры), графика не будет
    if len(result['top_lemmas']) == 0:
        await message.answer(format_result(result), reply_markup=after_analysis_buttons())
        return

    await message.answer(format_result(result))

    filename = f'data/chart_{message.from_user.id}.png'
    make_chart(result, filename)
    await message.answer_photo(
        FSInputFile(filename),
        caption='График по тексту',
        reply_markup=after_analysis_buttons(),
    )
    os.remove(filename)
