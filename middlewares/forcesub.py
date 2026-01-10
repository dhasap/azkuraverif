import time
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest
import config

class ForceSubMiddleware(BaseMiddleware):
    def __init__(self):
        # Cache sederhana: {user_id: {'status': bool, 'time': float}}
        self.cache = {}
        self.TTL = 120  # Cache duration dalam detik (2 Menit)

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Hanya jalankan untuk Message dan CallbackQuery
        if not isinstance(event, (types.Message, types.CallbackQuery)):
            return await handler(event, data)

        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        # Bypass untuk Admin (Opsional, tapi direkomendasikan agar admin tidak terkunci)
        if user.id in config.ADMIN_IDS:
            return await handler(event, data)

        # Cek Cache
        current_time = time.time()
        cached_data = self.cache.get(user.id)

        if cached_data and (current_time - cached_data['time'] < self.TTL):
            if cached_data['status']:
                return await handler(event, data)
            # Jika status cached False, lanjut ke kirim pesan error di bawah
        else:
            # Jika tidak ada di cache atau expired, Cek ke Telegram API
            try:
                member = await event.bot.get_chat_member(chat_id=config.FORCE_SUB_CHANNEL, user_id=user.id)

                # Status yang diizinkan
                if member.status in ['member', 'administrator', 'creator']:
                    self.cache[user.id] = {'status': True, 'time': current_time}
                    return await handler(event, data)
                else:
                    self.cache[user.id] = {'status': False, 'time': current_time}

            except TelegramBadRequest:
                # Jika bot bukan admin di channel atau channel tidak ketemu
                print(f"Error: Bot belum jadi admin di channel {config.FORCE_SUB_CHANNEL}")
                # Fail-safe: Izinkan user agar bot tidak macet total
                return await handler(event, data)
            except Exception as e:
                print(f"Force Sub Error: {e}")
                return await handler(event, data)

        # --- Jika User Belum Join ---

        # Siapkan Tombol
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Join Channel Utama", url=config.FORCE_SUB_URL)],
            [InlineKeyboardButton(text="🔄 Cek Status Join", callback_data="check_subscription")]
        ])

        # Kirim Pesan Peringatan
        if isinstance(event, types.Message):
            await event.answer(config.FORCE_SUB_MESSAGE, reply_markup=keyboard, parse_mode="HTML")
        elif isinstance(event, types.CallbackQuery):
            # Khusus jika user klik tombol "Cek Status" (looping logic)
            if event.data == "check_subscription":
                # Hapus cache untuk user ini agar pengecekan dilakukan ulang
                if user and user.id in self.cache:
                    del self.cache[user.id]

                # Coba cek ulang status keanggotaan
                try:
                    member = await event.bot.get_chat_member(chat_id=config.FORCE_SUB_CHANNEL, user_id=user.id)

                    if member.status in ['member', 'administrator', 'creator']:
                        # Jika sekarang user sudah join, simpan ke cache dan lanjutkan
                        current_time = time.time()
                        self.cache[user.id] = {'status': True, 'time': current_time}
                        await event.message.delete()  # Hapus pesan force sub
                        await event.answer("✅ Anda telah bergabung! Akses diberikan.", show_alert=False)

                        # Panggil handler untuk melanjutkan proses
                        return await handler(event, data)
                    else:
                        # Jika masih belum join, beri pesan
                        await event.answer("❌ Anda belum bergabung ke channel!", show_alert=True)
                except TelegramBadRequest:
                    await event.answer("❌ Gagal memeriksa status, coba lagi nanti.", show_alert=True)
                except Exception as e:
                    await event.answer("❌ Terjadi kesalahan saat memeriksa status.", show_alert=True)
            else:
                await event.answer("⚠️ Harap join channel dulu!", show_alert=True)
                # Kirim pesan baru agar terlihat
                await event.message.answer(config.FORCE_SUB_MESSAGE, reply_markup=keyboard, parse_mode="HTML")

        # Stop eksekusi handler (User diblokir)
        return
