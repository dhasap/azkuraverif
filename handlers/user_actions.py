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
    user_data = db.get_user(user_id)
    if not user_data:
        await callback.answer("Error: Data user tidak ditemukan.", show_alert=True)
        return

    # Generate Referral Link
    bot_info = await callback.bot.get_me()
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
    
    await callback.message.edit_text(profile_text, reply_markup=keyboards.profile_menu(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "action_checkin")
async def process_checkin(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
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
