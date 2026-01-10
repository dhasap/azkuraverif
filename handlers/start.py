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

@router.message(F.text == "🚀 Layanan Verifikasi")
async def show_verification_services(message: types.Message):
    """Handler untuk tombol navigasi bawah Layanan Verifikasi"""
    user_data = db.get_user(message.from_user.id)
    balance = user_data['balance'] if user_data else 0

    text = (
        f"🎯 <b>PILIH KATEGORI VERIFIKASI</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Saldo Anda:</b> {balance} Poin\n\n"
        f"Kami menyediakan berbagai layanan verifikasi:\n\n"
        f"🎵 <b>Musik & Streaming</b>\n"
        f"   • Spotify Premium Student\n"
        f"   • YouTube Premium Student\n\n"
        f"🎓 <b>Pendidikan</b>\n"
        f"   • K12 Teacher Verification\n"
        f"   • ChatGPT Education\n\n"
        f"🤖 <b>AI & Tools</b>\n"
        f"   • Google One/Bolt\n"
        f"   • Perplexity Pro\n\n"
        f"🎖️ <b>Militer</b>\n"
        f"   • Military/Veteran Verification\n\n"
        f"✨ <b>Pilih kategori yang Anda butuhkan:</b>"
    )

    kb = keyboards.service_categories()
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.message(F.text == "👤 Profil Saya")
async def show_profile(message: types.Message):
    """Handler untuk tombol navigasi bawah Profil Saya"""
    user = message.from_user
    user_data = db.get_user(user.id)
    balance = user_data['balance'] if user_data else 0
    full_name = user.first_name
    if user.last_name:
        full_name += f" {user.last_name}"

    username = f"@{user.username}" if user.username else "Tidak ada"

    text = (
        f"👤 <b>PROFIL PENGGUNA</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <b>Nama:</b> {full_name}\n"
        f"🆔 <b>ID Telegram:</b> {user.id}\n"
        f"👤 <b>Username:</b> {username}\n"
        f"💰 <b>Saldo Poin:</b> {balance}\n\n"
        f"📊 <b>Statistik:</b>\n"
        f"   • Verifikasi Berhasil: Belum Tersedia\n"
        f"   • Verifikasi Gagal: Belum Tersedia\n"
        f"   • Total Penggunaan: Belum Tersedia\n\n"
        f"✨ <b>Opsi Profil:</b>"
    )

    kb = keyboards.profile_menu()
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.message(F.text == "📅 Daily Check-in")
async def daily_checkin(message: types.Message):
    """Handler untuk tombol navigasi bawah Daily Check-in"""
    user_data = db.get_user(message.from_user.id)
    balance = user_data['balance'] if user_data else 0

    text = (
        f"🎁 <b>HADIAH HARIAN</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Saldo Anda:</b> {balance} Poin\n\n"
        f"🎯 <b>Hadiah Harian:</b>\n"
        f"   • Bonus harian untuk pengguna aktif\n"
        f"   • Hadiah: +{config.CHECKIN_REWARD} Poin\n"
        f"   • Klaim sekali per hari\n\n"
        f"⏰ <b>Waktu Tersisa:</b> Belum Tersedia\n\n"
        f"✨ <b>Gunakan hadiah harian untuk verifikasi:</b>"
    )

    kb = keyboards.main_menu()
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.message(F.text == "💎 Topup Poin")
async def topup_points(message: types.Message):
    """Handler untuk tombol navigasi bawah Topup Poin"""
    user_data = db.get_user(message.from_user.id)
    balance = user_data['balance'] if user_data else 0

    text = (
        f"💎 <b>MANAJEMEN POIN</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Saldo Anda:</b> {balance} Poin\n\n"
        f"🎯 <b>Opsi Manajemen:</b>\n"
        f"   • Topup Poin - Beli lebih banyak\n"
        f"   • Redeem Kode - Tukar kode hadiah\n"
        f"   • Referral - Undang teman & dapatkan poin\n\n"
        f"🎁 <b>Program Referral:</b>\n"
        f"   • Dapatkan +{config.REFERRAL_REWARD} Poin per pengguna baru\n"
        f"   • Bagikan link referral Anda\n\n"
        f"✨ <b>Pilih opsi di bawah ini:</b>"
    )

    kb = keyboards.main_menu()
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.message(F.text == "❓ Bantuan")
async def show_help(message: types.Message):
    """Handler untuk tombol navigasi bawah Bantuan"""
    text = (
        f"ℹ️ <b>PANDUAN & BANTUAN</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 <b>Cara Menggunakan Bot:</b>\n"
        f"   1. Pilih layanan verifikasi\n"
        f"   2. Siapkan link SheerID\n"
        f"   3. Proses otomatis akan berjalan\n"
        f"   4. Tunggu hasil verifikasi\n\n"
        f"💡 <b>Tips Sukses:</b>\n"
        f"   • Gunakan link resmi dari platform\n"
        f"   • Pastikan saldo cukup\n"
        f"   • Gunakan data valid\n\n"
        f"📞 <b>Dukungan:</b>\n"
        f"   • Hubungi admin jika ada masalah\n"
        f"   • Gabung channel untuk info terbaru\n\n"
        f"✨ <b>Butuh bantuan lebih lanjut?</b>"
    )

    kb = keyboards.main_menu()
    await message.answer(text, reply_markup=kb, parse_mode="HTML")
