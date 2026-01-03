from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from database_turso import db
import keyboards
import config

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    """Handler saat user mengetik /start"""
    user = message.from_user
    
    # --- MAINTENANCE CHECK ---
    if db.get_setting('maintenance_mode') == '1':
        user_db = db.get_user(user.id)
        is_admin = (user.id in config.ADMIN_IDS) or (user_db and user_db.get('is_admin'))
        if not is_admin:
            await message.answer("🛠 <b>SYSTEM MAINTENANCE</b>\n\nBot sedang dalam pemeliharaan sistem. Silakan coba beberapa saat lagi.", parse_mode="HTML")
            return
    # -------------------------
    
    # Cek Referral
    referrer_id = None
    args = command.args
    if args and args.isdigit():
        try:
            potential_id = int(args)
            # Self-referral check
            if potential_id != user.id:
                # Cek apakah referrer valid di DB (opsional tapi bagus)
                referrer_data = db.get_user(potential_id)
                if referrer_data:
                    referrer_id = potential_id
        except ValueError:
            pass

    # Register user ke database
    full_name = user.first_name
    if user.last_name:
        full_name += f" {user.last_name}"
        
    # create_user sekarang mengembalikan True jika user BARU berhasil dibuat
    is_new_user = db.create_user(user.id, user.username, full_name, invited_by=referrer_id)
    
    # Jika user baru dan ada referrer, notifikasi ke referrer
    if is_new_user and referrer_id:
        try:
            await message.bot.send_message(
                referrer_id,
                f"🎉 <b>Referral Baru!</b>\n\n"
                f"{full_name} telah mendaftar menggunakan link Anda.\n"
                f"Bonus: <b>+{config.REFERRAL_REWARD} Poin</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass # Referrer mungkin blokir bot

    # Ambil data user terbaru (untuk cek saldo dan admin status)
    user_data = db.get_user(user.id)
    balance = user_data['balance'] if user_data else 0
    is_admin = (user.id in config.ADMIN_IDS) or (user_data and user_data.get('is_admin'))

    # Pesan 1: Sapaan & Reply Keyboard (Navigasi Bawah)
    await message.answer(
        f"👋 Halo, <b>{full_name}</b>!\nSelamat datang di <b>{config.APP_NAME}</b>.",
        reply_markup=keyboards.get_main_keyboard(is_admin),
        parse_mode="HTML"
    )

    # Pesan 2: Menu Inline (Layanan)
    menu_text = (
        f"🤖 <b>DASHBOARD UTAMA</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Saldo Anda:</b> <code>{balance} Poin</code>\n\n"
        f"✨ <b>Layanan Tersedia:</b>\n"
        f"🎧 <b>Spotify Student</b> - 1 Poin\n"
        f"📺 <b>YouTube Premium</b> - 1 Poin\n"
        f"☁️ <b>OneDrive 1TB</b> - 2 Poin\n"
        f"🎓 <b>K12 Teacher</b> - 3 Poin\n\n"
        f"👇 <b>Silakan pilih menu di bawah ini:</b>"
    )

    await message.answer(menu_text, reply_markup=keyboards.main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "menu_home")
async def callback_home(callback: types.CallbackQuery):
    """Handler tombol kembali ke menu utama"""
    # Sama seperti start, tapi edit pesan (biar rapi)
    user = callback.from_user
    user_data = db.get_user(user.id)
    balance = user_data['balance'] if user_data else 0
    full_name = user.first_name

    text = (
        f"👋 Halo, <b>{full_name}</b>!\n\n"
        f"Selamat datang di <b>{config.APP_NAME}</b>.\n"
        f"Gunakan bot ini untuk melakukan verifikasi student discount dengan mudah.\n\n"
        f"💰 <b>Saldo Poin Anda:</b> {balance}\n\n"
        f"Silakan pilih layanan di bawah ini:"
    )
    
    await callback.message.edit_text(text, reply_markup=keyboards.main_menu(), parse_mode="HTML")
    await callback.answer()
