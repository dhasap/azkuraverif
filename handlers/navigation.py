from aiogram import Router, types, F
from database_turso import db
import keyboards
import config
from handlers import start, user_actions 

# Import admin filter
from handlers.admin import IsAdmin

router = Router()

@router.message(F.text == "🚀 Layanan Verifikasi")
async def nav_services(message: types.Message):
    user_data = db.get_user(message.from_user.id)
    balance = user_data['balance'] if user_data else 0
    
    text = (
        f"🤖 <b>KATALOG LAYANAN</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 <b>Saldo Anda:</b> <code>{balance} Poin</code>\n\n"
        f"✨ <b>Pilihan Layanan:</b>\n"
        f"🎧 <b>Spotify Student</b> (1 Poin)\n"
        f"📺 <b>YouTube Premium</b> (1 Poin)\n"
        f"☁️ <b>OneDrive / Bolt</b> (2 Poin)\n"
        f"🎓 <b>K12 Teacher</b> (3 Poin)\n\n"
        f"👇 <b>Klik tombol di bawah untuk memilih:</b>"
    )
    await message.answer(text, reply_markup=keyboards.main_menu(), parse_mode="HTML")

@router.message(F.text == "👤 Profil Saya")
async def nav_profile(message: types.Message):
    # Reuse logic from user_actions.show_profile but adapted for Message object
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    
    if not user_data:
        await message.reply("Data tidak ditemukan.")
        return

    bot_info = await message.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"

    profile_text = (
        f"👤 <b>KARTU PENGGUNA</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>ID Akun:</b> <code>{user_data['telegram_id']}</code>\n"
        f"🎩 <b>Nama:</b> {user_data['full_name']}\n"
        f"💰 <b>Saldo:</b> <code>{user_data['balance']} Poin</code>\n"
        f"📅 <b>Bergabung:</b> {user_data['created_at'].split(' ')[0]}\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"📢 <b>PROGRAM REFERRAL</b>\n"
        f"Undang teman dan dapatkan <b>+{config.REFERRAL_REWARD} Poin</b> gratis!\n\n"
        f"🔗 <b>Link Anda:</b>\n"
        f"<code>{ref_link}</code>\n"
        f"<i>(Klik link untuk menyalin)</i>"
    )
    await message.answer(profile_text, reply_markup=keyboards.profile_menu(), parse_mode="HTML")

@router.message(F.text == "📅 Daily Check-in")
async def nav_checkin(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
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
                f"✅ <b>CHECK-IN BERHASIL!</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"Selamat! Reward harian telah ditambahkan.\n"
                f"💰 Saldo Baru: <b>{new_bal} Poin</b>\n\n"
                f"<i>Jangan lupa kembali lagi besok!</i>"
            )
            await message.reply(msg, parse_mode="HTML")
        except Exception as e:
            await message.reply(f"Error: {e}")
        finally:
            conn.close()
    else:
        await message.reply("⏳ <b>Oops!</b>\nAnda sudah melakukan Check-in hari ini.\nSilakan kembali lagi besok untuk klaim reward.", parse_mode="HTML")

@router.message(F.text.in_({"💎 Topup Poin", "❓ Bantuan"}))
async def nav_info(message: types.Message):
    if "Topup" in message.text:
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
    else:
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

@router.message(F.text == "🛠 Admin Panel", IsAdmin())
async def nav_admin(message: types.Message):
    await message.answer(
        "🛠 <b>ADMIN DASHBOARD</b>\n\nSilakan pilih menu manajemen:", 
        reply_markup=keyboards.admin_dashboard_kb(),
        parse_mode="HTML"
    )
