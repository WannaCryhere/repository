from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
import config
from handlers import cmd_start, cmd_help, cmd_play, cmd_travel, cmd_stats, cmd_stop, handle_message

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# регистрация команд
dp.register_message_handler(cmd_start, commands=["start"]) 
dp.register_message_handler(cmd_help, commands=["help"]) 
dp.register_message_handler(cmd_play, commands=["play"]) 
dp.register_message_handler(cmd_travel, commands=["travel"]) 
dp.register_message_handler(cmd_stats, commands=["stats"]) 
dp.register_message_handler(cmd_stop, commands=["stop"]) 
# все остальные сообщения идут в общий обработчик
dp.register_message_handler(handle_message)


if __name__ == '__main__':
    print("Bot is starting...")
    executor.start_polling(dp, skip_updates=True)
