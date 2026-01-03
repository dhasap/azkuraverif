import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
from database_turso import db
from handlers import start, user_actions, verification, admin, navigation
from middlewares.forcesub import ForceSubMiddleware

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def main():
    # 1. Cek Token
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN tidak ditemukan! Pastikan sudah diset di file .env")
        return

    # 2. Inisialisasi Bot & Dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # --- Register Middlewares ---
    # Force Subscribe (Jalan sebelum handler apapun)
    fs_middleware = ForceSubMiddleware()
    dp.message.middleware(fs_middleware)
    dp.callback_query.middleware(fs_middleware)

    # 3. Register Routers
    dp.include_router(admin.router)
    dp.include_router(navigation.router) # Register navigation for text commands
    dp.include_router(start.router)
    dp.include_router(user_actions.router)
    dp.include_router(verification.router)

    # 4. Start Polling
    logger.info("🤖 Bot sedang berjalan...")
    
    # Hapus webhook jika ada (biar gak konflik sama polling)
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat polling: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot dihentikan.")
