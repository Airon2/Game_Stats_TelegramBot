from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from steam import Steam
from decouple import config

# Получаем ключ API Steam и токен Telegram из файла .env
steamTOKEN = config("STEAM_API_KEY")
TelegramTOKEN = config("TELEGRAM_API_TOKEN")

# Инициализируем клиент API Steam
steam = Steam(steamTOKEN)

# Определяем app ID для игр (ID игры в Steam)
squad_app_id = 393380
RON_app_id = 1144200
pubg_app_id = 578080

# Словарь для хранения состояния ожидания для каждого пользователя
user_states = {}

# Функция для проверки валидности Steam ID
def check_steamid(steam_id):
    return len(steam_id) == 17 and steam_id.isdigit()

# Функция для получения времени игры
def get_playtime(games, app_id):
    for game in games:
        if game.get('appid') == app_id:
            return game.get('playtime_forever', None)
    return None

# Функция для обработки команды /squadstats
async def squadstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_states[user_id] = 'waiting_for_squad_steam_id'
    await update.message.reply_text("Squad ойынының статистикасын алу үшін Steam ID енгізіңіз.")

# Функция для обработки команды /ronstats
async def ronstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_states[user_id] = 'waiting_for_ron_steam_id'
    await update.message.reply_text("Ready Or Not Статистикасын алу үшін Steam ID енгізіңіз.")

# Функция для обработки команды /pubgstats
async def pubgstats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_states[user_id] = 'waiting_for_pubg_steam_id'
    await update.message.reply_text("PUBG ойынының статистикасын алу үшін Steam ID енгізіңіз..")

# Функция для обработки сообщений с Steam ID
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    if user_states.get(user_id) == 'waiting_for_squad_steam_id':
        steam_id = update.message.text

        if not check_steamid(steam_id):
            await update.message.reply_text("Қате Steam ID. 17 таңбалы сандық кодты енгізіңіз.")
            return

        try:
            user_games = steam.users.get_owned_games(steam_id)
        except Exception as e:
            await update.message.reply_text(f"Ошибка получения данных о пользователе: {e}")
            return

        games = user_games.get('games', [])
        playtime_forever = get_playtime(games, squad_app_id)

        if playtime_forever is not None:
            playtime_hours = round(playtime_forever / 60, 1)
            await update.message.reply_text(f"Squad ойын уақыты: {playtime_hours:.1f} cағат")
        else:
            await update.message.reply_text("Squad ойыны пайдаланушының ойындар тізімінде жоқ.")
        
        user_states[user_id] = None  # Сбрасываем состояние после обработки сообщения

    elif user_states.get(user_id) == 'waiting_for_ron_steam_id':
        steam_id = update.message.text

        if not check_steamid(steam_id):
            await update.message.reply_text("Қате Steam ID. 17 таңбалы сандық кодты енгізіңіз.")
            return

        try:
            user_games = steam.users.get_owned_games(steam_id)
        except Exception as e:
            await update.message.reply_text(f"Ошибка получения данных о пользователе: {e}")
            return

        games = user_games.get('games', [])
        playtime_forever = get_playtime(games, RON_app_id)

        if playtime_forever is not None:
            playtime_hours = round(playtime_forever / 60, 1)
            await update.message.reply_text(f"Ready Or Not ойын уақыты: {playtime_hours:.1f} cағат")
        else:
            await update.message.reply_text("Ready Or Not ойыны пайдаланушының ойындар тізімінде жоқ")
        
        user_states[user_id] = None  # Сбрасываем состояние после обработки сообщения

    elif user_states.get(user_id) == 'waiting_for_pubg_steam_id':
        steam_id = update.message.text

        if not check_steamid(steam_id):
            await update.message.reply_text("Қате Steam ID. 17 таңбалы сандық кодты енгізіңіз.")
            return

        try:
            user_games = steam.users.get_owned_games(steam_id)
        except Exception as e:
            await update.message.reply_text(f"Ошибка получения данных о пользователе: {e}")
            return

        games = user_games.get('games', [])
        playtime_forever = get_playtime(games, pubg_app_id)

        if playtime_forever is not None:
            playtime_hours = round(playtime_forever / 60, 1)
            await update.message.reply_text(f"PUBG ойын уақыты: {playtime_hours:.1f} cағат")
        else:
            await update.message.reply_text("PUBG ойыны пайдаланушының ойындар тізімінде жоқ")
        
        user_states[user_id] = None  # Сбрасываем состояние после обработки сообщения

# Основная функция для запуска бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TelegramTOKEN).build()

    # Обработчики команд и сообщений
    app.add_handler(CommandHandler("squadstats", squadstats))
    app.add_handler(CommandHandler("ronstats", ronstats))
    app.add_handler(CommandHandler("pubgstats", pubgstats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    app.run_polling()
