from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.callback_data import CallbackData
from game import GameState
from data import countries

# тип user_id -> GameState
_games = {}


async def cmd_start(message: types.Message):
    await message.answer("🌍 Добро пожаловать! Используйте /play для одиночного вопроса, /travel для режима путешествия (10 стран), /stats — чтобы посмотреть очки, /help — помощь.")


async def cmd_help(message: types.Message):
    await message.answer("Команды:\n/start — старт\n/play — одиночный вопрос\n/travel — начать путешествие\n/stats — показать текущие очки и жизни\n/stop — завершить текущую игру")


async def cmd_play(message: types.Message):
    # одиночный вопрос (не сохраняем прогресс в GameState)
    country = choice(list(countries.keys()))
    capital = countries[country]["capital"]
    # prepare options
    other_caps = [countries[c]["capital"] for c in sample(list(countries.keys()), 3)]
    options = list(set(other_caps + [capital]))
    from aiogram.types import ReplyKeyboardMarkup
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        keyboard.add(opt)
    # store temporary state тут
    _games[message.from_user.id] = GameState(message.from_user.id, countries)
    gs = _games[message.from_user.id]
    gs.current_country = country
    gs.current_capital = capital
    gs.in_travel = False
    await message.answer(f"✈️ Вы прилетели в {country}!\nКакая столица?", reply_markup=keyboard)


async def cmd_travel(message: types.Message):
    user_id = message.from_user.id
    gs = GameState(user_id, countries)
    gs.start_travel()
    _games[user_id] = gs
    country, capital = gs.next_question()
    options = [countries[c]["capital"] for c in sample(list(countries.keys()), 3)] + [capital]
    options = list(set(options))
    from aiogram.types import ReplyKeyboardMarkup
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for opt in options:
        keyboard.add(opt)
    await message.answer(f"🧳 Путешествие началось! Страна 1: {country}\nКакая столица?\n(У вас {gs.lives} жизней)", reply_markup=keyboard)


async def cmd_stats(message: types.Message):
    user_id = message.from_user.id
    gs = _games.get(user_id)
    if not gs:
        await message.answer("У вас нет активной игры. Напишите /travel чтобы начать.")
        return
    await message.answer(f"📊 Ваши очки: {gs.score}\nЖизни: {gs.lives}\nПройдено: {gs.progress}/{len(gs.route) if gs.route else 0}")


async def cmd_stop(message: types.Message):
    user_id = message.from_user.id
    gs = _games.pop(user_id, None)
    if not gs:
        await message.answer("Активная игра не найдена.")
    else:
        await message.answer(f"Игра остановлена. Ваш итог: {gs.score} очков.")


async def handle_message(message: types.Message):
    user_id = message.from_user.id
    gs = _games.get(user_id)
    text = message.text.strip()
    if not gs or (not gs.current_capital):
        await message.answer("Напишите /play или /travel чтобы начать игру.")
        return

    # если игрок в режиме путешествия, мы используем GameState.answer
    correct = text.lower() == (gs.current_capital or "").lower()
    country = gs.current_country
    fact = countries.get(country, {}).get("fact", "")

    if gs.in_travel:
        correct, finished = gs.answer(text)
        if correct:
            reply = f"✅ Верно! +10 очков.\nℹ️ Факт о {country}: {fact}\nОчки: {gs.score} | Жизни: {gs.lives}"
        else:
            reply = f"❌ Неверно. Правильный ответ: {gs.current_capital}.\nℹ️ Факт о {country}: {fact}\nОчки: {gs.score} | Жизни: {gs.lives}"
        if finished:
            # путешествие завершено (либо кончились жизни, либо маршрут пройден)
            _games.pop(user_id, None)
            reply += f"\n\n🏁 Путешествие завершено! Итог: {gs.score} очков."
            from aiogram.types import ReplyKeyboardRemove
            await message.answer(reply, reply_markup=ReplyKeyboardRemove())
        else:
            # следующий вопрос
            country_next, capital_next = gs.next_question()
            options = [countries[c]["capital"] for c in sample(list(countries.keys()), 3)] + [capital_next]
            options = list(set(options))
            from aiogram.types import ReplyKeyboardMarkup
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for opt in options:
                keyboard.add(opt)
            await message.answer(reply + f"\n\nСледующая страна: {country_next}. Какая столица?", reply_markup=keyboard)
    else:
        # это одиночный режим
        if correct:
            await message.answer(f"✅ Верно! +10 очков.\nℹ️ Факт: {fact}")
        else:
            await message.answer(f"❌ Неверно. Правильный ответ: {gs.current_capital}.\nℹ️ Факт: {fact}")
        # удалить временный GameState
        _games.pop(user_id, None)