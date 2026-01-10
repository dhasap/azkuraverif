from aiogram import Router, types, F
from database_turso import db
import keyboards
import config
from handlers import start, user_actions 

# Import admin filter
from handlers.admin import IsAdmin

router = Router()

@router.message(F.text == "💎 Topup Poin")
async def nav_topup(message: types.Message):
    text = (
        "💎 <b>PUSAT TOPUP</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        "1 Poin = Rp 1.000 (Contoh Rate)\n\n"
        "🛒 <b>Cara Membeli Saldo:</b>\n"
        "1. Hubungi Admin Resmi kami via link di bawah.\n"
        "2. Transfer pembayaran (QRIS/E-Wallet/Bank).\n"
        "3. Admin akan memberikan <b>Kode Voucher</b> atau mengisi saldo Anda.\n\n"
        f"📞 <b>Kontak Admin:</b> {config.SUPPORT_URL}\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "🎟 <b>Sudah punya Kode Voucher?</b>\n"
        "Masuk ke menu <b>Profil Saya</b> -> <b>Topup / Redeem</b> untuk menukarkan kode."
    )
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

@router.message(F.text == "❓ Bantuan")
async def nav_help(message: types.Message):
    text = (
        "❓ <b>PUSAT BANTUAN & PANDUAN</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "📘 <b>Cara Menggunakan Bot:</b>\n"
        "1. Pilih menu <b>🚀 Layanan Verifikasi</b>.\n"
        "2. Pilih jenis layanan (misal: Spotify).\n"
        "3. Dapatkan link verifikasi dari website resmi layanan (SheerID).\n"
        "4. Kirim link tersebut ke bot ini.\n"
        "5. Tunggu proses verifikasi selesai otomatis.\n\n"
        "📙 <b>Pertanyaan Umum (FAQ):</b>\n"
        "• <b>Saldo habis?</b> Lakukan Check-in harian atau Topup.\n"
        "• <b>Verifikasi gagal?</b> Poin otomatis dikembalikan.\n"
        "• <b>Undang teman?</b> Gunakan link di menu Profil.\n\n"
        f"📞 <b>Butuh Bantuan Lebih Lanjut?</b>\n"
        f"Hubungi: {config.SUPPORT_URL}\n"
        f"Channel Info: {config.CHANNEL_URL}"
    )
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

@router.message(F.text == "🛠 Admin Panel")
async def nav_admin(message: types.Message):
    # Cek apakah user adalah admin
    user_id = message.from_user.id
    user_db = db.get_user(user_id)
    is_admin = (user_id in config.ADMIN_IDS) or (user_db and user_db.get('is_admin'))

    if not is_admin:
        await message.answer("❌ <b>ACCESS DENIED</b>\nAnda tidak memiliki akses ke panel admin.", parse_mode="HTML")
        return

    await message.answer(
        "🛠 <b>ADMIN DASHBOARD</b>\n\nSilakan pilih menu manajemen:",
        reply_markup=keyboards.admin_dashboard_kb(),
        parse_mode="HTML"
    )

@router.message(F.text == "🎯 Verifikasi Spesial")
async def nav_special_verification(message: types.Message):
    user_data = db.get_user(message.from_user.id)
    balance = user_data['balance'] if user_data else 0

    text = (
        f"🎯 <b>VERIFIKASI SPESIAL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Saldo Anda:</b> {balance} Poin\n\n"
        f"✨ <b>Layanan Premium:</b>\n"
        f"   • Military/Veteran Verification\n"
        f"   • K12 Teacher Verification\n"
        f"   • ChatGPT Education\n\n"
        f"🎯 <b>Fitur Unggulan:</b>\n"
        f"   • Proses otomatis maksimal\n"
        f"   • Data valid terotentikasi\n"
        f"   • Kecepatan maksimum\n\n"
        f"🔒 <b>Keamanan:</b>\n"
        f"   • Enkripsi data maksimum\n"
        f"   • Proteksi identitas\n"
        f"   • Privasi terjamin\n\n"
        f"✨ <b>Pilih layanan spesial di bawah ini:</b>"
    )
    kb = keyboards.military_services()
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.message(F.text == "🎁 Daily Bonus")
async def nav_daily_bonus(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)

    # Cek apakah user ditemukan
    if not user:
        await message.reply("❌ <b>ERROR:</b> Akun tidak ditemukan di database.", parse_mode="HTML")
        return

    # Cek tanggal (Sama seperti user_actions.py)
    last_checkin_str = user.get('last_checkin')
    can_checkin = False

    from datetime import datetime
    if not last_checkin_str:
        can_checkin = True
    else:
        try:
            last_date = datetime.fromisoformat(last_checkin_str).date() if 'T' in last_checkin_str else datetime.strptime(last_checkin_str.split('.')[0], "%Y-%m-%d %H:%M:%S").date()
            if last_date < datetime.now().date():
                can_checkin = True
        except Exception:
            can_checkin = True

    if can_checkin:
        conn = db.get_connection()
        try:
            conn.execute(
                "UPDATE users SET balance = balance + ?, last_checkin = CURRENT_TIMESTAMP WHERE telegram_id = ?",
                (config.CHECKIN_REWARD, user_id)
            )
            conn.commit()

            new_bal = user['balance'] + config.CHECKIN_REWARD
            msg = (
                f"🎁 <b>DAILY BONUS BERHASIL!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎉 Selamat! Bonus harian telah ditambahkan.\n"
                f"💰 Saldo Baru: <b>{new_bal} Poin</b>\n\n"
                f"✨ <b>Keuntungan Bonus Harian:</b>\n"
                f"   • Gratis setiap hari\n"
                f"   • Tidak ada batas klaim\n"
                f"   • Tambah saldo Anda\n\n"
                f"⏰ <b>Ingat:</b> Kembali besok untuk klaim bonus baru!"
            )
            await message.reply(msg, parse_mode="HTML")
        except Exception as e:
            await message.reply(f"❌ <b>Error:</b> {e}", parse_mode="HTML")
        finally:
            conn.close()
    else:
        await message.reply("⏳ <b>MOHON TUNGGU</b>\n\nAnda sudah mengklaim bonus harian hari ini.\n\n⏰ <b>Waktu tersisa:</b> Klaim kembali besok!", parse_mode="HTML")

@router.message(F.text == "💎 Manajemen Poin")
async def nav_point_management(message: types.Message):
    user_data = db.get_user(message.from_user.id)
    balance = user_data['balance'] if user_data else 0

    text = (
        f"💎 <b>MANAJEMEN POIN LENGKAP</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Saldo Saat Ini:</b> {balance} Poin\n\n"
        f"🎯 <b>Opsi Manajemen:</b>\n"
        f"   • Topup Poin - Beli lebih banyak\n"
        f"   • Redeem Kode - Tukar kode hadiah\n"
        f"   • Referral - Undang teman & dapatkan poin\n\n"
        f"🎁 <b>Program Referral:</b>\n"
        f"   • Dapatkan +{config.REFERRAL_REWARD} Poin per pengguna baru\n"
        f"   • Bagikan link referral Anda\n\n"
        f"📊 <b>Statistik Penggunaan:</b>\n"
        f"   • Verifikasi: Belum Tersedia\n"
        f"   • Bonus Harian: Belum Tersedia\n\n"
        f"✨ <b>Pilih opsi manajemen di bawah:</b>"
    )
    kb = keyboards.main_menu()
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@router.message(F.text == "ℹ️ Informasi")
async def nav_information(message: types.Message):
    text = (
        f"ℹ️ <b>INFORMASI LENGKAP</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 <b>Nama Bot:</b> {config.APP_NAME}\n"
        f"🆔 <b>ID Bot:</b> {message.bot.id}\n"
        f"✨ <b>Versi:</b> 2.0.0 Premium\n\n"
        f"🎯 <b>Layanan Utama:</b>\n"
        f"   • Spotify Premium Student\n"
        f"   • YouTube Premium Student\n"
        f"   • K12 Teacher Verification\n"
        f"   • Military/Veteran Verification\n"
        f"   • Google One/Bolt.new\n"
        f"   • Perplexity Pro Student\n\n"
        f"🏆 <b>Keunggulan Kami:</b>\n"
        f"   • Proses otomatis cepat\n"
        f"   • Data valid terotentikasi\n"
        f"   • Keamanan maksimum\n"
        f"   • Dukungan 24/7\n\n"
        f"📞 <b>Kontak & Dukungan:</b>\n"
        f"   • Channel: {config.CHANNEL_URL}\n"
        f"   • Support: {config.SUPPORT_URL}\n\n"
        f"🔒 <b>Privasi & Keamanan:</b>\n"
        f"   • Enkripsi data end-to-end\n"
        f"   • Perlindungan identitas\n"
        f"   • Kebijakan privasi ketat"
    )
    kb = keyboards.main_menu()
    await message.answer(text, reply_markup=kb, parse_mode="HTML", disable_web_page_preview=True)
