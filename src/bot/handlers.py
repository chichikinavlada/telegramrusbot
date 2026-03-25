from __future__ import annotations

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from src.bot.keyboards import glavnoe_menu, knopka_nazad, knopki_posle_analiza, knopki_posle_razdela
from src.services.analyzer import AnalizatorTeksta, RezultatAnaliza
from src.services.charts import postroit_grafik
from src.services.database import BazaDannyh

router = Router()

TEXT_POMOSCHI = (
    "Я разбираю русский учебный текст.\n\n"
    "Могу посчитать слова и предложения, показать частотные леммы, найти сущности и сохранить результат в историю.\n\n"
    "Нажми «Разобрать текст», потом просто пришли кусок текста длиной хотя бы 30 символов."
)


def setup_handlers(database: BazaDannyh, analyzer: AnalizatorTeksta) -> Router:
    zhdu_tekst_ot: set[int] = set()

    async def pokazat_menu(message: Message, text: str | None = None) -> None:
        privet = (
            text
            or "Привет. Это бот, который разбирает русский учебный текст. Выбери, что тебе нужно."
        )
        await message.answer(privet, reply_markup=glavnoe_menu())

    async def obnovit_soobshenie(callback: CallbackQuery, text: str, *, markup) -> None:
        if not callback.message:
            await callback.answer()
            return

        try:
            await callback.message.edit_text(text, reply_markup=markup)
        except TelegramBadRequest:
            await callback.message.answer(text, reply_markup=markup)
        await callback.answer()

    @router.callback_query(F.data == "menu:home")
    async def menu_home(callback: CallbackQuery) -> None:
        await obnovit_soobshenie(
            callback,
            "Вот меню. Можешь выбрать нужный раздел.",
            markup=glavnoe_menu(),
        )

    @router.callback_query(F.data == "menu:help")
    async def menu_help(callback: CallbackQuery) -> None:
        await obnovit_soobshenie(callback, TEXT_POMOSCHI, markup=knopka_nazad())

    @router.callback_query(F.data == "menu:analiz")
    async def menu_analiz(callback: CallbackQuery) -> None:
        if callback.from_user:
            zhdu_tekst_ot.add(callback.from_user.id)
        await obnovit_soobshenie(
            callback,
            "Пришли учебный текст одним сообщением, я его разберу.",
            markup=knopka_nazad(),
        )

    @router.callback_query(F.data == "menu:history")
    async def menu_history(callback: CallbackQuery) -> None:
        if not callback.from_user:
            await callback.answer()
            return

        analizy = database.get_recent_analyses(callback.from_user.id)
        if not analizy:
            text = "История пока пустая. Сначала разберите хотя бы один текст."
        else:
            stroki: list[str] = ["Последние анализы:"]
            for nomer, item in enumerate(analizy, start=1):
                lemmmy = ", ".join(lemma for lemma, _ in item["top_lemmas"][:3]) or "нет"
                stroki.append(
                    f"{nomer}) {item['created_at']} | слов {item['word_count']} | "
                    f"предложений {item['sentence_count']} | леммы {lemmmy}"
                )
            text = "\n".join(stroki)

        await obnovit_soobshenie(callback, text, markup=knopki_posle_razdela())

    @router.callback_query(F.data == "menu:stats")
    async def menu_stats(callback: CallbackQuery) -> None:
        if not callback.from_user:
            await callback.answer()
            return

        stats = database.get_user_stats(callback.from_user.id)
        await obnovit_soobshenie(
            callback,
            "Твоя статистика:\n"
            f"Анализов всего: {stats['total_analyses']}\n"
            f"Средний размер текста: {stats['avg_word_count']} слов",
            markup=knopki_posle_razdela(),
        )

    @router.message(F.text)
    async def vse_soobsheniya(message: Message) -> None:
        if not message.from_user or not message.text:
            return

        user_id = message.from_user.id
        text = message.text.strip()

        if text.startswith("/"):
            await pokazat_menu(
                message,
                "Тут все через кнопки, так что просто выбери действие в меню.",
            )
            return

        nado_analizirovat = user_id in zhdu_tekst_ot or len(text) >= 30

        if not nado_analizirovat:
            await message.answer(
                "Текст слишком короткий. Пришли хотя бы 30 символов.",
                reply_markup=knopka_nazad(),
            )
            return

        zhdu_tekst_ot.discard(user_id)
        wait_message = await message.answer("Секунду, смотрю текст...")
        result = analyzer.analiz(text)
        database.save_analysis(
            user_id=user_id,
            username=message.from_user.username,
            result=result,
        )

        await wait_message.delete()
        await message.answer(format_rezultat(result), reply_markup=knopki_posle_analiza())

        chart = postroit_grafik(result)
        image = BufferedInputFile(chart.getvalue(), filename="analysis.png")
        await message.answer_photo(image, caption="Вот график по тексту", reply_markup=knopki_posle_analiza())

    return router


def format_rezultat(result: RezultatAnaliza) -> str:
    lemmas = ", ".join(f"{lemma} ({count})" for lemma, count in result.top_lemmas[:10]) or "нет данных"
    entities = format_sushchnosti(result)

    return (
        "Готово, вот что получилось.\n"
        f"Слов: {result.word_count}\n"
        f"Предложений: {result.sentence_count}\n"
        f"Частотные леммы: {lemmas}\n"
        f"Сущности: {entities}"
    )


def format_sushchnosti(result: RezultatAnaliza) -> str:
    if not result.entities:
        return "не найдены"

    chunks: list[str] = []
    grouped: dict[str, list[str]] = {}
    for item in result.entities:
        grouped.setdefault(item.label, []).append(item.value)

    for label, values in grouped.items():
        unique_values = ", ".join(values[:4])
        suffix = "..." if len(values) > 4 else ""
        chunks.append(f"{label}: {unique_values}{suffix}")
    return "; ".join(chunks)
