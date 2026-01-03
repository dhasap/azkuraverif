"""Tool Pemeriksaan Akses dan Verifikasi"""
import logging
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import CHANNEL_USERNAME

logger = logging.getLogger(__name__)


def is_group_chat(update: Update) -> bool:
    """Cek apakah ini chat grup"""
    chat = update.effective_chat
    return chat and chat.type in ("group", "supergroup")


async def reject_group_command(update: Update) -> bool:
    """Batasan grup: hanya izinkan /verify /verify2 /verify3 /verify4 /verify5 /qd"""
    if is_group_chat(update):
        await update.message.reply_text("Chat grup hanya mendukung /verify /verify2 /verify3 /verify4 /verify5 /qd, silakan chat pribadi untuk perintah lainnya.")
        return True
    return False


async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Cek apakah user sudah join channel"""
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError as e:
        logger.error("Cek member channel gagal: %s", e)
        return False
