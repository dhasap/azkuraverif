import asyncio
import json
import os
import random
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
from services.military.sheerid_verifier import SheerIDVerifier as MilitaryVerifier
from services.perplexity.sheerid_verifier import SheerIDVerifier as PerplexityVerifier

router = Router()

class VerifyState(StatesGroup):
    waiting_for_url = State()
    waiting_for_email = State()
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
    "military": {
        "name": "Military / Veteran",
        "verifier": MilitaryVerifier,
        "cost": 3
    },
    "one": {
        "name": "OneDrive / Bolt",
        "verifier": OneVerifier, 
        "cost": 2
    },
    "perplexity": {
        "name": "Perplexity Pro (Student)",
        "verifier": PerplexityVerifier,
        "cost": 2
    },
    "chatgpt": {
        "name": "ChatGPT (Auto-Detect)",
        "verifier": None, # Placeholder
        "cost": 0 # Determined later
    }
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
        f"🔗 <b>VERIFIKASI: {service_name.upper()}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Ikuti langkah berikut:\n\n"
        f"1️⃣ Buka halaman offer resmi.\n"
        f"2️⃣ <b>JANGAN ISI DATA APAPUN!</b>\n"
        f"3️⃣ Salin URL saat formulir masih kosong.\n\n"
        f"⬇️ <b>Kirimkan Link URL tersebut di sini:</b>"
    )
    # Tombol batal
    cancel_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="❌ Batal", callback_data="cancel_verify")]]
    )
    
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

    # --- LOGIKA AUTO-DETECT (KHUSUS CHATGPT) ---
    if service_key == 'chatgpt':
        url_lower = url.lower()
        detected_service = None
        
        # Cek Keyword di URL
        if any(x in url_lower for x in ['teacher', 'faculty', 'k12', 'school']):
            detected_service = 'k12'
        elif any(x in url_lower for x in ['military', 'veteran', 'active_duty', 'reservist']):
            detected_service = 'military'
        
        if not detected_service:
            detected_service = 'military' 
            await message.answer("⚠️ Tipe verifikasi tidak terdeteksi otomatis. Menggunakan mode <b>MILITARY</b>.", parse_mode="HTML")
        
        service_key = detected_service
        await state.update_data(service=service_key)

    # -------------------------------------------

    # Cek verification ID via method static di Class Verifier
    VerifierClass = SERVICES[service_key]['verifier']
    verif_id = VerifierClass.parse_verification_id(url)
    
    # YouTubeVerifier dan BoltVerifier support auto-create session via URL
    if not verif_id and VerifierClass not in [BoltVerifier, YouTubeVerifier]:
        await message.reply("❌ <b>Gagal membaca ID Verifikasi.</b>\nPastikan Anda menyalin link lengkap dari halaman SheerID.", parse_mode="HTML")
        return
        
    await state.update_data(verification_id=verif_id, original_url=url)

    # KHUSUS MILITARY: Coba ambil data valid, jika tidak ada gunakan Random Generator
    if service_key == 'military':
        try:
            vets_file = 'data/veterans.json'
            if os.path.exists(vets_file):
                with open(vets_file, 'r') as f:
                    vets = json.load(f)
                
                if vets:
                    # Pilih satu data valid secara acak
                    selected_vet = random.choice(vets)
                    await state.update_data(custom_inputs=selected_vet)
                    
                    formatted_info = (
                        f"🎖 <b>DATA VETERAN VALID TERPILIH:</b>\n"
                        f"👤 Nama: {selected_vet.get('first_name')} {selected_vet.get('last_name')}\n"
                        f"📅 Tgl Lahir: {selected_vet.get('birth_date')}\n"
                        f"⚔️ Branch: {selected_vet.get('branch')}\n"
                        f"📜 Discharge: {selected_vet.get('discharge_date')}\n"
                    )
                    await message.answer(f"✅ Link diterima.\n\n{formatted_info}", parse_mode="HTML")
                else:
                     await message.answer("⚠️ Database veteran kosong. Menggunakan <b>DATA ACAK</b> (Peluang sukses lebih rendah).", parse_mode="HTML")
            else:
                await message.answer("⚠️ Database veteran tidak ditemukan. Menggunakan <b>DATA ACAK</b> (Peluang sukses lebih rendah).", parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error reading veterans db: {e}")
            await message.answer("⚠️ Gagal membaca database. Menggunakan <b>DATA ACAK</b>.", parse_mode="HTML")
    
    # Khusus YouTube: Tanya Email agar tersambung ke akun Google user
    if service_key == 'youtube':
        await state.set_state(VerifyState.waiting_for_email)
        text = (
            "📧 <b>KONFIRMASI EMAIL</b>\n"
            "━━━━━━━━━━━━━━━━\n"
            "Untuk YouTube Premium, Anda wajib menggunakan email yang sama dengan akun Google Anda.\n\n"
            "👉 <b>Masukkan alamat email Google/YouTube Anda:</b>"
        )
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎲 Gunakan Email Acak (.edu)", callback_data="skip_email")],
            [types.InlineKeyboardButton(text="❌ Batal", callback_data="cancel_verify")]
        ])
        await message.answer(text, reply_markup=kb, parse_mode="HTML")
        return

    # Lanjut ke Konfirmasi (Layanan Lain)
    await proceed_to_confirm(message, state, service_key, verif_id)

@router.callback_query(F.data == "skip_email", VerifyState.waiting_for_email)
async def skip_email(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await proceed_to_confirm(callback.message, state, data['service'], data.get('verification_id'))
    await callback.answer()

@router.message(VerifyState.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        await message.reply("❌ Format email tidak valid!")
        return
    
    await state.update_data(user_email=email)
    data = await state.get_data()
    await proceed_to_confirm(message, state, data['service'], data.get('verification_id'))

async def proceed_to_confirm(message, state, service_key, verif_id):
    """Helper untuk menampilkan konfirmasi akhir"""
    await state.set_state(VerifyState.confirm_process)
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

    id_display = verif_id if verif_id else "(Auto Detect)"
    email_display = data.get('user_email', "Otomatis (.edu)")
    confirm_text = (
        f"📝 <b>KONFIRMASI PESANAN</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Layanan:</b> {SERVICES[service_key]['name']}\n"
        f"💸 <b>Biaya:</b> {cost} Poin\n"
        f"📧 <b>Email:</b> <code>{email_display}</code>\n"
        f"🆔 <b>ID:</b> <code>{id_display}</code>\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        "Apakah data sudah benar? Proses tidak dapat dibatalkan setelah ini."
    )
    
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ PROSES SEKARANG", callback_data="do_verify")],
        [types.InlineKeyboardButton(text="❌ Batal", callback_data="cancel_verify")]]
    )
    
    await message.answer(confirm_text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data == "do_verify", VerifyState.confirm_process)
async def execute_verification(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    service_key = data['service']
    verif_id = data.get('verification_id')
    original_url = data.get('original_url')
    user_email = data.get('user_email')
    custom_inputs = data.get('custom_inputs', {}) 
    
    cost = SERVICES[service_key]['cost']
    user_id = callback.from_user.id
    
    if not db.deduct_balance(user_id, cost):
        await callback.answer("Saldo tidak cukup!", show_alert=True)
        await state.clear()
        return

    await callback.message.edit_text(
        "⏳ <b>SEDANG MEMPROSES...</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        "🔹 Menyiapkan data valid...\n"
        "🔹 Generate dokumen resmi...\n"
        "🔹 Upload ke server SheerID...\n\n"
        "<i>Mohon tunggu 15-45 detik. Jangan tutup chat ini.</i>",
        parse_mode="HTML"
    )
    
    try:
        VerifierClass = SERVICES[service_key]['verifier']
        # YouTube dan Bolt butuh URL asli untuk auto-session / parsing parameter
        if VerifierClass in [BoltVerifier, YouTubeVerifier]:
            verifier = VerifierClass(original_url)
            # BoltVerifier might accept verification_id separately, but YouTubeVerifier now takes url in __init__
            # To be safe for Bolt legacy signature:
            if VerifierClass == BoltVerifier:
                 verifier = VerifierClass(original_url, verification_id=verif_id)
        else:
            verifier = VerifierClass(verif_id)
        
        # Kirim Proxy khusus Perplexity jika ada di config
        verify_kwargs = {**custom_inputs}
        if user_email:
            verify_kwargs["email"] = user_email
            
        if service_key == "perplexity" and config.PERPLEXITY_PROXY:
            verify_kwargs["proxy"] = config.PERPLEXITY_PROXY
            
        result = await verifier.verify(**verify_kwargs)
        
        if result['success']:
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
        db.add_balance(user_id, cost)
        await callback.message.edit_text(f"❌ <b>SISTEM ERROR</b>\n\nTerjadi kesalahan internal: {str(e)}\nSaldo telah dikembalikan.", reply_markup=keyboards.back_home(), parse_mode="HTML")
    
    finally:
        await state.clear()