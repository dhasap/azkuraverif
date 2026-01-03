from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Menu Navigasi Bawah (Persistent)"""
    kb = [
        [KeyboardButton(text="🚀 Layanan Verifikasi")],
        [KeyboardButton(text="👤 Profil Saya"), KeyboardButton(text="📅 Daily Check-in")],
        [KeyboardButton(text="💎 Topup Poin"), KeyboardButton(text="❓ Bantuan")]
    ]
    
    if is_admin:
        kb.append([KeyboardButton(text="🛠 Admin Panel")])
        
    return ReplyKeyboardMarkup(
        keyboard=kb, 
        resize_keyboard=True, 
        input_field_placeholder="Pilih menu navigasi..."
    )

def admin_dashboard_kb() -> InlineKeyboardMarkup:
    """Menu Dashboard Admin (Inline)"""
    kb = [
        [
            InlineKeyboardButton(text="📊 Statistik", callback_data="admin_stats"),
            InlineKeyboardButton(text="🔧 Maintenance", callback_data="admin_maint_toggle")
        ],
        [
            InlineKeyboardButton(text="📢 Info Broadcast", callback_data="admin_broadcast_help"),
            InlineKeyboardButton(text="➕ Info Add Poin", callback_data="admin_addpoint_help")
        ],
        [InlineKeyboardButton(text="❌ Tutup Panel", callback_data="admin_close")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def main_menu() -> InlineKeyboardMarkup:
    """Keyboard Menu Utama"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎧 Spotify", callback_data="service_spotify"),
            InlineKeyboardButton(text="📺 YouTube", callback_data="service_youtube"),
        ],
        [
            InlineKeyboardButton(text="🧠 ChatGPT / Service", callback_data="service_chatgpt"),
            InlineKeyboardButton(text="☁️ One / Bolt", callback_data="service_one"),
        ],
        [
            InlineKeyboardButton(text="👤 Profil Saya", callback_data="menu_profile"),
            InlineKeyboardButton(text="💳 Topup / Redeem", callback_data="menu_topup"),
        ],
        [
            InlineKeyboardButton(text="💳 Topup / Redeem", callback_data="menu_topup"),
            InlineKeyboardButton(text="📅 Daily Check-in", callback_data="action_checkin"),
        ],
        [
            InlineKeyboardButton(text="📢 Channel", url="https://t.me/azkura_channel"), # Ganti nanti
            InlineKeyboardButton(text="❓ Bantuan", callback_data="menu_help"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_home() -> InlineKeyboardMarkup:
    """Tombol kembali ke menu utama"""
    keyboard = [[InlineKeyboardButton(text="🔙 Kembali ke Menu Utama", callback_data="menu_home")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_verify(service_name: str, cost: int) -> InlineKeyboardMarkup:
    """Tombol konfirmasi sebelum verifikasi"""
    keyboard = [
        [InlineKeyboardButton(text=f"✅ Lanjut ({cost} Poin)", callback_data=f"start_{service_name}")],
        [InlineKeyboardButton(text="❌ Batal", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def profile_menu() -> InlineKeyboardMarkup:
    """Menu di dalam Profil"""
    keyboard = [
        [InlineKeyboardButton(text="📜 Riwayat Transaksi", callback_data="history_tx")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
