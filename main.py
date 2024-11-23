# main.py

import asyncio
from config.config_manager import ConfigManager
from bot.quotex_bot import QuotexBot
from core.utils import configure_logging
from quotexapi.config import email, password


async def main():
    configure_logging()

    config_manager = ConfigManager()
    config = config_manager.get_config()
    credentials = config_manager.get_credentials()
    telegram_token = config_manager.get_telegram_token()

    config_manager.init_audio()

    bot = QuotexBot(
        email=email,
        password=password,
        config=config,
        telegram_token=telegram_token,
        telegram_chat_id=credentials["telegram_chat_id"],
    )

    if await bot.connect():
        await bot.run()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        loop.close()
