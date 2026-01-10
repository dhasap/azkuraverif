from datetime import datetime, date
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database_turso import db
import keyboards
import config

router = Router()

class RedeemState(StatesGroup):
    waiting_for_code = State()

@router.callback_query(F.data == "menu_profile")
async def show_profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    full_name = callback.from_user.first_name
    if callback.from_user.last_name:
        full_name += f" {callback.from_user.last_name}"

    # Pastikan pengguna terdaftar di database
    user_data = db.get_user(user_id)
    if not user_data:
        # Pengguna belum terdaftar, daftarkan mereka
        is_new_user = db.create_user(user_id, username, full_name)
        if is_new_user:
            print(f"User {user_id} berhasil didaftarkan")
        else:
            print(f"Gagal mendaftarkan user {user_id}")

    # Ambil data pengguna setelah memastikan mereka terdaftar
    user_data = db.get_user(user_id)
    if not user_data:
        await callback.answer("Error: Gagal mengakses data pengguna setelah registrasi.", show_alert=True)
        return

    # Generate Referral Link
    bot_info = await callback.bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"

    profile_text = (
        f"👤 <b>PROFIL PENGGUNA LENGKAP</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ <b>Nama Lengkap:</b> {user_data['full_name']}\n"
        f"🆔 <b>ID Telegram:</b> <code>{user_data['telegram_id']}</code>\n"
        f"👤 <b>Username:</b> @{callback.from_user.username or 'Tidak Ada'}\n"
        f"💰 <b>Saldo Poin:</b> <code>{user_data['balance']} Poin</code>\n"
        f"📅 <b>Tanggal Bergabung:</b> {user_data['created_at'].split(' ')[0]}\n\n"
        f"🎯 <b>Status:</b> {'Admin' if user_data.get('is_admin') else 'User Biasa'}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🏆 <b>PRESTASI & RANKING</b>\n"
        f"   • Verifikasi Berhasil: Belum Tersedia\n"
        f"   • Verifikasi Gagal: Belum Tersedia\n"
        f"   • Referral Berhasil: Belum Tersedia\n\n"
        f"📢 <b>PROGRAM REFERRAL</b>\n"
        f"   • Dapatkan <b>+{config.REFERRAL_REWARD} Poin</b> per pengguna baru\n"
        f"   • Bagikan link referral Anda:\n"
        f"   <code>{ref_link}</code>\n\n"
        f"🔒 <b>PRIVASI & KEAMANAN</b>\n"
        f"   • Data terlindungi\n"
        f"   • Enkripsi aktif\n"
        f"   • Privasi terjaga\n\n"
        f"✨ <b>Opsi Profil:</b>"
    )

    await callback.message.edit_text(profile_text, reply_markup=keyboards.profile_menu(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "action_checkin")
async def process_checkin(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username
    full_name = callback.from_user.first_name
    if callback.from_user.last_name:
        full_name += f" {callback.from_user.last_name}"

    # Pastikan pengguna terdaftar di database
    user_data = db.get_user(user_id)
    if not user_data:
        # Pengguna belum terdaftar, daftarkan mereka
        is_new_user = db.create_user(user_id, username, full_name)
        if is_new_user:
            print(f"User {user_id} berhasil didaftarkan")
        else:
            print(f"Gagal mendaftarkan user {user_id}")

    # Ambil data pengguna setelah memastikan mereka terdaftar
    user = db.get_user(user_id)

    # Cek apakah user ditemukan (seharusnya selalu ditemukan setelah registrasi)
    if not user:
        await callback.answer("❌ Gagal mengakses data pengguna setelah registrasi.", show_alert=True)
        return

    # Cek tanggal checkin terakhir
    last_checkin_str = user.get('last_checkin')
    can_checkin = False

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

            await callback.answer(f"🎉 Check-in Sukses! +{config.CHECKIN_REWARD} Poin.", show_alert=True)
            # Refresh dengan pesan baru
            new_bal = user['balance'] + config.CHECKIN_REWARD

            msg = (
                f"✅ <b>CHECK-IN BERHASIL!</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"Anda mendapatkan reward harian.\n"
                f"💰 Saldo Baru: <b>{new_bal} Poin</b>\n\n"
                f"<i>Kembali lagi besok untuk reward lainnya!</i>"
            )
            # Kita kirim pesan baru saja karena edit pesan menu utama agak tricky logicnya di sini
            await callback.message.answer(msg, parse_mode="HTML")

        except Exception as e:
            await callback.answer(f"Gagal check-in: {e}", show_alert=True)
        finally:
            conn.close()
    else:
        await callback.answer("⏳ Oops! Anda sudah check-in hari ini. Coba lagi besok ya!", show_alert=True)

@router.callback_query(F.data == "menu_topup")
async def menu_topup(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "💎 <b>ISI ULANG SALDO (TOPUP)</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        "1 Poin = Rp 1.000 (Contoh)\n\n"
        "🛒 <b>Cara Membeli Voucher:</b>\n"
        "1. Hubungi Admin Resmi kami.\n"
        "2. Lakukan pembayaran (QRIS/E-Wallet).\n"
        "3. Anda akan mendapatkan <b>Kode Voucher</b>.\n\n"
        f"📞 <b>Kontak Admin:</b> {config.SUPPORT_URL}\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "🎟 <b>Punya Kode Voucher?</b>\n"
        "Kirimkan kode Anda sekarang di chat ini untuk klaim poin otomatis."
    )
    
    # Set state menunggu input
    await state.set_state(RedeemState.waiting_for_code)
    
    # Beri tombol batal
    cancel_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="❌ Batal Redeem", callback_data="cancel_redeem")]
    ])
    
    await callback.message.edit_text(text, reply_markup=cancel_kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "cancel_redeem")
async def cancel_redeem(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Redeem dibatalkan.")
    # Kembali ke home
    # Kita panggil handler home (perlu import circular kalau panggil fungsi start.py)
    # Jadi kita kirim pesan baru atau edit text manual
    await callback.message.edit_text("Redeem dibatalkan. Silakan pilih menu:", reply_markup=keyboards.main_menu())

@router.message(RedeemState.waiting_for_code)
async def process_redeem_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    user_id = message.from_user.id
    
    # Proses redeem di DB
    result = db.redeem_card(user_id, code)
    
    if result['success']:
        await message.answer(f"✅ <b>BERHASIL!</b>\n\nSaldo Anda bertambah +{result['amount']} Poin.", parse_mode="HTML")
    else:
        await message.answer(f"❌ <b>GAGAL:</b> {result['message']}", parse_mode="HTML")
    
    await state.clear()
    # Tampilkan menu utama lagi
    await message.answer("Menu Utama:", reply_markup=keyboards.main_menu())

# --- Additional Handlers ---

@router.callback_query(F.data == "history_tx")
async def show_history(callback: types.CallbackQuery):
    """Menampilkan riwayat transaksi (Verifikasi & Redeem)"""
    history = db.get_transaction_history(callback.from_user.id)

    if not history:
        await callback.answer("Belum ada riwayat transaksi.", show_alert=True)
        return

    text = "📜 <b>RIWAYAT TRANSAKSI (10 Terakhir)</b>\n━━━━━━━━━━━━━━━━\n\n"

    for item in history:
        # Format: [ICON] Tipe - Nama (Waktu)
        # Type: verify / redeem
        date_str = item['created_at'].split('.')[0] # Hapus microsecond

        if item['type'] == 'verify':
            icon = "✅" if item['status'] == 'success' else "❌"
            desc = f"Verifikasi {item['description']}"
        else:
            icon = "💎" # Redeem
            desc = f"Redeem Voucher"

        text += f"{icon} <b>{desc}</b>\n└ 📅 {date_str}\n\n"

    await callback.message.edit_text(text, reply_markup=keyboards.profile_menu(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "achievements")
async def show_achievements(callback: types.CallbackQuery):
    """Menampilkan prestasi dan ranking pengguna"""
    text = (
        f"🏆 <b>PRESTASI & RANKING</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 <b>Prestasi Anda:</b>\n"
        f"   • Verifikasi Berhasil: 0\n"
        f"   • Verifikasi Gagal: 0\n"
        f"   • Referral Berhasil: 0\n"
        f"   • Bonus Harian: 0\n\n"
        f"🌟 <b>Pencapaian:</b>\n"
        f"   • Pengguna Baru: ❌\n"
        f"   • Verifikator Pro: ❌\n"
        f"   • Master Referral: ❌\n"
        f"   • Daily Streak: ❌\n\n"
        f"📊 <b>Peringkat Global:</b>\n"
        f"   • Peringkat: #0 dari 0 pengguna\n\n"
        f"✨ <b>Cara Mendapatkan Prestasi:</b>\n"
        f"   • Selesaikan verifikasi pertama\n"
        f"   • Ajak teman menggunakan referral\n"
        f"   • Klaim bonus harian\n"
        f"   • Gunakan bot secara rutin\n\n"
        f"🎁 <b>Hadiah Prestasi:</b>\n"
        f"   • Bonus poin eksklusif\n"
        f"   • Akses fitur premium\n"
        f"   • Ranking khusus"
    )

    await callback.message.edit_text(text, reply_markup=keyboards.profile_menu(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "settings")
async def show_settings(callback: types.CallbackQuery):
    """Menampilkan pengaturan akun"""
    text = (
        f"⚙️ <b>PENGATURAN AKUN</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔔 <b>Notifikasi:</b>\n"
        f"   • Status: Aktif\n"
        f"   • Verifikasi: Diaktifkan\n"
        f"   • Promosi: Diaktifkan\n\n"
        f"🔄 <b>Auto-Claim:</b>\n"
        f"   • Bonus Harian: Dinonaktifkan\n"
        f"   • Referral Bonus: Diaktifkan\n\n"
        f"💳 <b>Metode Pembayaran:</b>\n"
        f"   • Default: Manual Transfer\n"
        f"   • Alternatif: Kode Voucher\n\n"
        f"🌐 <b>Bahasa:</b>\n"
        f"   • Saat Ini: Indonesia\n\n"
        f"🔒 <b>Privasi:</b>\n"
        f"   • Mode Privasi: Standar\n"
        f"   • Data Sharing: Diizinkan\n\n"
        f"🔧 <b>Pengaturan Tambahan:</b>\n"
        f"   • Backup Data: Tidak Aktif\n"
        f"   • Export Riwayat: Tidak Tersedia\n\n"
        f"✨ <b>Pengaturan akan segera diperbarui!</b>"
    )

    await callback.message.edit_text(text, reply_markup=keyboards.profile_menu(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "check_subscription")
async def confirm_subscription(callback: types.CallbackQuery):
    """
    Handler ini HANYA akan terpanggil jika user SUDAH join channel.
    Jika belum join, Middleware akan memblokir dan tidak sampai ke sini.
    """
    await callback.answer("✅ Terima kasih sudah bergabung!", show_alert=True)
    await callback.message.delete()
    # Tampilkan menu utama
    await callback.message.answer("🎉 <b>Akses Terbuka!</b>\nSilakan gunakan bot.", reply_markup=keyboards.main_menu(), parse_mode="HTML")
