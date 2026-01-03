import asyncio
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database_turso import db
import keyboards
import config

# Import service modules
from services.spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from services.youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from services.k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from services.one.sheerid_verifier import SheerIDVerifier as OneVerifier
from services.Boltnew.sheerid_verifier import SheerIDVerifier as BoltVerifier

router = Router()

class VerifyState(StatesGroup):
    waiting_for_url = State()
    confirm_process = State()

# Mapping nama service ke Verifier Class & Config
SERVICES = {
    "spotify": {
        "name": "Spotify Premium Student",
        "verifier": SpotifyVerifier,
        "cost": 1
    },
    "youtube": {
        "name": "YouTube Premium Student",
        "verifier": YouTubeVerifier,
        "cost": 1
    },
    "k12": {
        "name": "K12 Teacher Verification",
        "verifier": K12Verifier,
        "cost": 3
    },
    "one": {
        "name": "OneDrive / Bolt",
        "verifier": OneVerifier, 
        "cost": 2
    },
    # Boltnew (Guru) bisa ditambahkan jika nanti dibuatkan menu khususnya
    # cost: 3
}

@router.callback_query(F.data.startswith("service_"))
async def select_service(callback: types.CallbackQuery, state: FSMContext):
    # --- MAINTENANCE CHECK ---
    if db.get_setting('maintenance_mode') == '1':
        user_id = callback.from_user.id
        user_db = db.get_user(user_id)
        is_admin = (user_id in config.ADMIN_IDS) or (user_db and user_db.get('is_admin'))
        if not is_admin:
            await callback.answer("⚠️ Maintenance Mode Active", show_alert=True)
            return
    # -------------------------

    service_key = callback.data.split("_")[1]
    
    if service_key not in SERVICES:
        await callback.answer("Layanan belum tersedia.", show_alert=True)
        return

    await state.update_data(service=service_key)
    await state.set_state(VerifyState.waiting_for_url)
    
    service_name = SERVICES[service_key]['name']
    
    text = (
        f"🎧 <b>VERIFIKASI: {service_name.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Ikuti langkah berikut untuk mendapatkan link:\n\n"
        f"1️⃣ Buka halaman offer resmi {service_name}.\n"
        f"2️⃣ Isi formulir awal hingga masuk ke halaman SheerID.\n"
        f"3️⃣ <b>Salin URL</b> dari address bar browser Anda.\n\n"
        f"✅ <b>Contoh URL Valid:</b>\n"
        f"<code>https://services.sheerid.com/verify/...</code>\n"
        f"<code>https://spotify.sheerid.com/...</code>\n\n"
        f"⬇️ <b>Kirimkan Link URL tersebut di sini:</b>"
    )
    # Tombol batal
    cancel_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="❌ Batal", callback_data="cancel_verify")]
    ])
    
    await callback.message.edit_text(text, reply_markup=cancel_kb, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "cancel_verify")
async def cancel_verify(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🚫 <b>Verifikasi Dibatalkan.</b>\nSilakan pilih menu lain.", reply_markup=keyboards.main_menu(), parse_mode="HTML")

@router.message(VerifyState.waiting_for_url)
async def process_url(message: types.Message, state: FSMContext):
    url = message.text.strip()
    data = await state.get_data()
    service_key = data['service']
    
    # Validasi URL (Basic)
    if "http" not in url:
        await message.reply("❌ <b>Link Invalid!</b>\nHarus diawali dengan <code>http://</code> atau <code>https://</code>.", parse_mode="HTML")
        return

    # Cek verification ID via method static di Class Verifier
    VerifierClass = SERVICES[service_key]['verifier']
    verif_id = VerifierClass.parse_verification_id(url)
    
    if not verif_id and VerifierClass != BoltVerifier:
        await message.reply("❌ <b>Gagal membaca ID Verifikasi.</b>\nPastikan Anda menyalin link lengkap dari halaman SheerID.", parse_mode="HTML")
        return
        
    # Simpan ID dan URL
    await state.update_data(verification_id=verif_id, original_url=url)
    
    # Tampilkan konfirmasi biaya
    cost = SERVICES[service_key]['cost']
    user_data = db.get_user(message.from_user.id)
    
    if user_data['balance'] < cost:
        await message.answer(
            f"⚠️ <b>SALDO TIDAK CUKUP</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"💰 Biaya Layanan: <b>{cost} Poin</b>\n"
            f"👛 Saldo Anda: <b>{user_data['balance']} Poin</b>\n\n"
            "💡 <i>Solusi: Lakukan Check-in harian atau Topup saldo.</i>",
            reply_markup=keyboards.back_home(),
            parse_mode="HTML"
        )
        await state.clear()
        return

    await state.set_state(VerifyState.confirm_process)
    
    id_display = verif_id if verif_id else "(Auto Detect)"
    
    confirm_text = (
        f"📝 <b>KONFIRMASI PESANAN</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Layanan:</b> {SERVICES[service_key]['name']}\n"
        f"💸 <b>Biaya:</b> {cost} Poin\n"
        f"🆔 <b>ID:</b> <code>{id_display}</code>\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        "Apakah data sudah benar? Proses tidak dapat dibatalkan setelah ini."
    )
    
    # Keyboard Yes/No
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ PROSES SEKARANG", callback_data="do_verify")],
        [types.InlineKeyboardButton(text="❌ Batal", callback_data="cancel_verify")]
    ])
    
    await message.answer(confirm_text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "do_verify", VerifyState.confirm_process)
async def execute_verification(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_key = data['service']
    verif_id = data.get('verification_id')
    original_url = data.get('original_url')
    cost = SERVICES[service_key]['cost']
    user_id = callback.from_user.id
    
    # 1. Deduct Balance (Atomic Check)
    if not db.deduct_balance(user_id, cost):
        await callback.answer("Saldo tidak cukup!", show_alert=True)
        await state.clear()
        return

    # Update UI: Processing
    await callback.message.edit_text(
        "⏳ <b>SEDANG MEMPROSES...</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        "🔹 Membuat identitas digital...\n"
        "🔹 Generate dokumen valid...\n"
        "🔹 Upload ke server SheerID...\n\n"
        "<i>Mohon tunggu 15-45 detik. Jangan tutup chat ini.</i>",
        parse_mode="HTML"
    )
    
    try:
        # 2. Call Service (Async)
        VerifierClass = SERVICES[service_key]['verifier']
        
        # Instansiasi Verifier
        if VerifierClass == BoltVerifier:
            verifier = VerifierClass(original_url, verification_id=verif_id)
        else:
            verifier = VerifierClass(verif_id)
        
        # Eksekusi verify
        result = await verifier.verify()
        
        # 3. Handle Result
        if result['success']:
            # Log success
            db.add_verification(user_id, service_key, "success", str(result))
            
            success_msg = (
                f"✅ <b>VERIFIKASI SUKSES!</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"🎉 Selamat! Dokumen telah disetujui.\n\n"
                f"📋 <b>Status:</b> {result['message']}\n"
            )
            if result.get('redirect_url'):
                success_msg += f"🔗 <b>Link Akses:</b> <a href='{result['redirect_url']}'>KLIK DISINI</a>\n"
            
            if result.get('reward_code'):
                success_msg += f"🎟 <b>Kode Promo:</b> <code>{result['reward_code']}</code>\n"
            
            success_msg += "\n<i>Terima kasih telah menggunakan layanan Azkura Verify!</i>"
            
            await callback.message.edit_text(success_msg, reply_markup=keyboards.back_home(), parse_mode="HTML", disable_web_page_preview=True)
            
        else:
            # Refund jika gagal sistem
            db.add_balance(user_id, cost) 
            db.add_verification(user_id, service_key, "failed", str(result))
            
            fail_msg = (
                f"❌ <b>VERIFIKASI GAGAL</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"Sistem gagal memverifikasi permintaan Anda.\n\n"
                f"⚠️ <b>Alasan:</b> {result['message']}\n\n"
                f"♻️ <b>Refund:</b> {cost} Poin telah dikembalikan ke saldo Anda.\n"
                f"<i>Silakan coba lagi dengan link baru.</i>"
            )
            await callback.message.edit_text(fail_msg, reply_markup=keyboards.back_home(), parse_mode="HTML")

    except Exception as e:
        # Crash handling
        db.add_balance(user_id, cost) # Refund
        await callback.message.edit_text(f"❌ <b>SISTEM ERROR</b>\n\nTerjadi kesalahan internal: {str(e)}\nSaldo telah dikembalikan.", reply_markup=keyboards.back_home(), parse_mode="HTML")
    
    finally:
        await state.clear()