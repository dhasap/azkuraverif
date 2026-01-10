import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject, BaseFilter
from database_turso import db
import config
import keyboards

router = Router()

class IsAdmin(BaseFilter):
    """Filter untuk mengecek apakah user adalah admin"""
    async def __call__(self, message: types.Message) -> bool:
        user_id = message.from_user.id
        # Handle CallbackQuery (karena BaseFilter bisa terima message atau callback)
        # Tapi di aiogram 3, filter callback agak beda. 
        # Untuk simplifikasi, kita asumsikan ini dipakai di Message filter.
        # Untuk Callback, kita cek manual atau buat filter overload.
        
        # 1. Cek dari Config (Super Admin)
        if user_id in config.ADMIN_IDS:
            return True
        # 2. Cek dari Database
        user = db.get_user(user_id)
        return user and user.get('is_admin')

# --- Message Handlers ---

@router.message(Command("addpoint"), IsAdmin())
async def cmd_addpoint(message: types.Message, command: CommandObject):
    """Tambah saldo user. Usage: /addpoint <user_id> <amount>"""
    if not command.args:
        await message.reply("⚠️ <b>Format Salah</b>\nGunakan: <code>/addpoint <user_id> <amount></code>", parse_mode="HTML")
        return

    try:
        args = command.args.split()
        if len(args) != 2:
            raise ValueError
        
        target_id = int(args[0])
        amount = int(args[1])
        
        if db.add_balance(target_id, amount):
            msg = (
                f"✅ <b>TOPUP SUKSES</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"👤 Target: <code>{target_id}</code>\n"
                f"💰 Jumlah: <b>{amount} Poin</b>\n"
                f"📅 Waktu: {asyncio.get_event_loop().time()}"
            )
            await message.reply(msg, parse_mode="HTML")
            
            # Opsional: Notifikasi ke user
            try:
                user_msg = (
                    f"🎁 <b>GIFT DITERIMA</b>\n"
                    f"━━━━━━━━━━━━━━━━\n"
                    f"Admin telah menambahkan saldo ke akun Anda.\n\n"
                    f"➕ <b>{amount} Poin</b>\n"
                    f"<i>Selamat menikmati layanan kami!</i>"
                )
                await message.bot.send_message(target_id, user_msg, parse_mode="HTML")
            except:
                pass 
        else:
            await message.reply("❌ <b>Gagal Update Database.</b>\nPastikan ID User benar dan terdaftar.", parse_mode="HTML")
            
    except ValueError:
        await message.reply("⚠️ <b>Input Invalid</b>\nPastikan ID dan Amount adalah angka.", parse_mode="HTML")

@router.message(Command("stats"), IsAdmin())
async def cmd_stats(message: types.Message):
    """Lihat statistik bot"""
    stats = db.get_stats()
    maint_status = db.get_setting('maintenance_mode')
    maint_icon = "🔴 ON" if maint_status == '1' else "🟢 OFF"
    
    # Hitung rate sukses
    total = stats['verifications']
    success = stats['success']
    failed = total - success
    rate = f"{(success/total)*100:.1f}%" if total > 0 else "0%"

    text = (
        "📊 <b>EXECUTIVE DASHBOARD</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "👥 <b>Basis Pengguna</b>\n"
        f"• Total User: <b>{stats['users']}</b>\n\n"
        "📝 <b>Performa Verifikasi</b>\n"
        f"• Total Request: <b>{total}</b>\n"
        f"• ✅ Berhasil: <b>{success}</b>\n"
        f"• ❌ Gagal: <b>{failed}</b>\n"
        f"• 📈 Success Rate: <b>{rate}</b>\n\n"
        "⚙️ <b>Status Sistem</b>\n"
        f"• Maintenance: <b>{maint_icon}</b>"
    )
    await message.reply(text, parse_mode="HTML")

@router.message(Command("maintenance"), IsAdmin())
async def cmd_maintenance(message: types.Message, command: CommandObject):
    """Set maintenance mode. Usage: /maintenance on|off"""
    status = command.args.lower().strip() if command.args else ""
    
    if status not in ["on", "off"]:
        current = "ON" if db.get_setting('maintenance_mode') == '1' else "OFF"
        await message.reply(
            f"🛠 <b>PENGATURAN MAINTENANCE</b>\n"
            f"Status Saat Ini: <b>{current}</b>\n\n"
            f"Gunakan command:\n"
            f"<code>/maintenance on</code> - Aktifkan (Kunci Bot)\n"
            f"<code>/maintenance off</code> - Matikan (Buka Bot)", 
            parse_mode="HTML"
        )
        return

    val = "1" if status == "on" else "0"
    db.set_setting("maintenance_mode", val)
    
    icon = "🔴" if status == "on" else "🟢"
    msg = (
        f"🛠 <b>MAINTENANCE UPDATE</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"Status Baru: <b>{status.upper()}</b> {icon}\n"
        f"<i>{'User tidak dapat akses layanan.' if status=='on' else 'Layanan dibuka untuk publik.'}</i>"
    )
    await message.reply(msg, parse_mode="HTML")

@router.message(Command("addadmin"), IsAdmin())
async def cmd_addadmin(message: types.Message, command: CommandObject):
    """Angkat user jadi admin. Usage: /addadmin <user_id>"""
    if not command.args:
        await message.reply("⚠️ Gunakan: <code>/addadmin <user_id></code>", parse_mode="HTML")
        return

    try:
        target_id = int(command.args.strip())
        if db.set_admin(target_id, True):
            await message.reply(
                f"✅ <b>ADMIN DITAMBAHKAN</b>\n"
                f"User ID: <code>{target_id}</code>\n"
                f"Sekarang memiliki akses penuh ke panel admin.", 
                parse_mode="HTML"
            )
        else:
            await message.reply("❌ Gagal update database.", parse_mode="HTML")
    except ValueError:
        await message.reply("⚠️ User ID harus angka.", parse_mode="HTML")

@router.message(Command("broadcast"), IsAdmin())
async def cmd_broadcast(message: types.Message, command: CommandObject):
    """Broadcast pesan ke semua user. Reply ke pesan atau ketik pesan setelah command."""
    # Tentukan konten pesan
    msg_to_send = None

    # Jika reply
    if message.reply_to_message:
        msg_to_send = message.reply_to_message
    # Jika ada teks argumen
    elif command.args:
        msg_to_send = command.args
    else:
        await message.reply(
            "📢 <b>BROADCAST MANAGER</b>\n"
            "━━━━━━━━━━━━━━━━\n"
            "Kirim pesan massal ke seluruh user.\n\n"
            "<b>Cara Pakai:</b>\n"
            "1. Reply pesan apapun dengan <code>/broadcast</code>\n"
            "2. Atau ketik: <code>/broadcast Pesan Anda</code>",
            parse_mode="HTML"
        )
        return

    users = db.get_all_users()
    total = len(users)
    sent = 0
    blocked = 0

    status_msg = await message.reply(f"⏳ <b>Sedang Mengirim...</b>\nTarget: {total} User", parse_mode="HTML")

    for uid in users:
        try:
            if isinstance(msg_to_send, str):
                await message.bot.send_message(uid, msg_to_send)
            else:
                await msg_to_send.copy_to(uid)
            sent += 1
        except Exception as e:
            blocked += 1
            # Log error jika perlu untuk debugging
            print(f"Broadcast error to {uid}: {str(e)}")

        # Hindari flood limit
        if sent % 20 == 0:
            await asyncio.sleep(1)

    await status_msg.edit_text(
        f"✅ <b>BROADCAST SELESAI</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🎯 Target Total: <b>{total}</b>\n"
        f"📨 Terkirim: <b>{sent}</b>\n"
        f"🚫 Gagal/Blokir: <b>{blocked}</b>",
        parse_mode="HTML"
    )

# --- Callback Handlers (Dashboard) ---

@router.callback_query(F.data == "admin_stats")
async def cb_stats(callback: types.CallbackQuery):
    # Cek admin manual karena filter IsAdmin mungkin belum support callback object
    user_id = callback.from_user.id
    user_db = db.get_user(user_id)
    if user_id not in config.ADMIN_IDS and not (user_db and user_db.get('is_admin')):
        await callback.answer("Access Denied", show_alert=True)
        return

    stats = db.get_stats()
    maint_status = db.get_setting('maintenance_mode')
    maint_icon = "🔴 ON" if maint_status == '1' else "🟢 OFF"
    
    total = stats['verifications']
    success = stats['success']
    failed = total - success
    rate = f"{(success/total)*100:.1f}%" if total > 0 else "0%"
    
    text = (
        "📊 <b>EXECUTIVE DASHBOARD</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "👥 <b>Basis Pengguna</b>\n"
        f"• Total User: <b>{stats['users']}</b>\n\n"
        "📝 <b>Performa Verifikasi</b>\n"
        f"• Total Request: <b>{total}</b>\n"
        f"• ✅ Berhasil: <b>{success}</b>\n"
        f"• ❌ Gagal: <b>{failed}</b>\n"
        f"• 📈 Success Rate: <b>{rate}</b>\n\n"
        "⚙️ <b>Status Sistem</b>\n"
        f"• Maintenance: <b>{maint_icon}</b>"
    )
    # Edit pesan yang ada
    await callback.message.edit_text(text, reply_markup=keyboards.admin_dashboard_kb(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "admin_maint_toggle")
async def cb_maint_toggle(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_db = db.get_user(user_id)
    if user_id not in config.ADMIN_IDS and not (user_db and user_db.get('is_admin')):
        await callback.answer("Access Denied", show_alert=True)
        return

    current = db.get_setting('maintenance_mode')
    new_val = "0" if current == "1" else "1"
    db.set_setting("maintenance_mode", new_val)
    
    status_text = "DIAKTIFKAN 🔴" if new_val == "1" else "DIMATIKAN 🟢"
    await callback.answer(f"Mode Maintenance: {status_text}")
    
    # Refresh stats view
    await cb_stats(callback)

@router.callback_query(F.data == "admin_broadcast_help")
async def cb_bc_help(callback: types.CallbackQuery):
    await callback.message.answer(
        "📢 <b>PANDUAN BROADCAST</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        "1. Kirim pesan yang ingin disebar ke chat ini.\n"
        "2. Reply pesan tersebut dan ketik <code>/broadcast</code>\n\n"
        "<i>Atau gunakan format langsung:</i>\n"
        "<code>/broadcast Pesan pengumuman di sini...</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_addpoint_help")
async def cb_addpoint_help(callback: types.CallbackQuery):
    await callback.message.answer(
        "➕ <b>PANDUAN ADD POINT</b>\n"
        "━━━━━━━━━━━━━━━━\n"
        "Gunakan format command berikut:\n"
        "<code>/addpoint [ID_USER] [JUMLAH]</code>\n\n"
        "Contoh:\n"
        "<code>/addpoint 123456789 10</code>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "admin_close")
async def cb_close(callback: types.CallbackQuery):
    await callback.message.delete()
