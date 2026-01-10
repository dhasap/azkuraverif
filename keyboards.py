from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import config

def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Menu Navigasi Bawah (Persistent) - Desain Elegan"""
    kb = [
        [KeyboardButton(text="🚀 Layanan Verifikasi"), KeyboardButton(text="🎁 Promo Spesial")],
        [KeyboardButton(text="👤 Profil Saya"), KeyboardButton(text="📅 Daily Check-in")],
        [KeyboardButton(text="💎 Topup Poin"), KeyboardButton(text="❓ Bantuan")]
    ]

    if is_admin:
        kb.append([KeyboardButton(text="🔐 Admin Panel")])

    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Pilih menu untuk memulai..."
    )

def admin_dashboard_kb() -> InlineKeyboardMarkup:
    """Menu Dashboard Admin (Inline) - Desain Profesional"""
    kb = [
        [
            InlineKeyboardButton(text="📈 Statistik Real-Time", callback_data="admin_stats"),
            InlineKeyboardButton(text="⚙️ Sistem Control", callback_data="admin_maint_toggle")
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast Massal", callback_data="admin_broadcast_help"),
            InlineKeyboardButton(text="💰 Manajemen Poin", callback_data="admin_addpoint_help")
        ],
        [InlineKeyboardButton(text="🔒 Tutup Panel", callback_data="admin_close")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def main_menu() -> InlineKeyboardMarkup:
    """Keyboard Menu Utama - Desain Premium"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎵 Spotify Premium", callback_data="service_spotify"),
            InlineKeyboardButton(text="🎬 YouTube Premium", callback_data="service_youtube"),
        ],
        [
            InlineKeyboardButton(text="🧠 Perplexity Pro", callback_data="service_perplexity"),
            InlineKeyboardButton(text="🤖 Google One/Bolt", callback_data="service_one"),
        ],
        [
            InlineKeyboardButton(text="👨‍🏫 K12 Teacher", callback_data="service_k12"),
            InlineKeyboardButton(text="🎖️ Military/Veteran", callback_data="service_military"),
        ],
        [
            InlineKeyboardButton(text="👤 Profil Saya", callback_data="menu_profile"),
            InlineKeyboardButton(text="🎁 Daily Check-in", callback_data="action_checkin"),
        ],
        [
            InlineKeyboardButton(text="💳 Topup & Redeem", callback_data="menu_topup"),
            InlineKeyboardButton(text="❓ Panduan & Bantuan", callback_data="menu_help"),
        ],
        [
            InlineKeyboardButton(text="📢 Join Channel", url=config.CHANNEL_URL),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def service_categories() -> InlineKeyboardMarkup:
    """Kategori Layanan - Desain Interaktif"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎵 Musik & Streaming", callback_data="cat_music"),
            InlineKeyboardButton(text="🎓 Pendidikan", callback_data="cat_education"),
        ],
        [
            InlineKeyboardButton(text="🤖 AI & Tools", callback_data="cat_ai"),
            InlineKeyboardButton(text="🎖️ Militer", callback_data="cat_military"),
        ],
        [
            InlineKeyboardButton(text="🔙 Kembali", callback_data="menu_home"),
            InlineKeyboardButton(text="🔍 Lihat Semua", callback_data="cat_all"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def music_services() -> InlineKeyboardMarkup:
    """Layanan Musik & Streaming"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎵 Spotify Student", callback_data="service_spotify"),
            InlineKeyboardButton(text="🎬 YouTube Premium", callback_data="service_youtube"),
        ],
        [
            InlineKeyboardButton(text="🔙 Kembali", callback_data="verify_now"),
            InlineKeyboardButton(text="🏠 Menu Utama", callback_data="menu_home"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def education_services() -> InlineKeyboardMarkup:
    """Layanan Pendidikan"""
    keyboard = [
        [
            InlineKeyboardButton(text="👨‍🏫 K12 Teacher", callback_data="service_k12"),
            InlineKeyboardButton(text="🤖 ChatGPT", callback_data="service_chatgpt"),
        ],
        [
            InlineKeyboardButton(text="🔙 Kembali", callback_data="verify_now"),
            InlineKeyboardButton(text="🏠 Menu Utama", callback_data="menu_home"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def ai_services() -> InlineKeyboardMarkup:
    """Layanan AI & Tools"""
    keyboard = [
        [
            InlineKeyboardButton(text="🤖 Google One", callback_data="service_one"),
            InlineKeyboardButton(text="🧠 Perplexity Pro", callback_data="service_perplexity"),
        ],
        [
            InlineKeyboardButton(text="🔙 Kembali", callback_data="verify_now"),
            InlineKeyboardButton(text="🏠 Menu Utama", callback_data="menu_home"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def military_services() -> InlineKeyboardMarkup:
    """Layanan Militer"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎖️ Military/Veteran", callback_data="service_military"),
        ],
        [
            InlineKeyboardButton(text="🔙 Kembali", callback_data="verify_now"),
            InlineKeyboardButton(text="🏠 Menu Utama", callback_data="menu_home"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def all_services() -> InlineKeyboardMarkup:
    """Semua Layanan dalam Satu Tampilan"""
    keyboard = [
        [
            InlineKeyboardButton(text="🎵 Spotify", callback_data="service_spotify"),
            InlineKeyboardButton(text="🎬 YouTube", callback_data="service_youtube"),
        ],
        [
            InlineKeyboardButton(text="👨‍🏫 K12", callback_data="service_k12"),
            InlineKeyboardButton(text="🤖 One/Bolt", callback_data="service_one"),
        ],
        [
            InlineKeyboardButton(text="🧠 Perplexity", callback_data="service_perplexity"),
            InlineKeyboardButton(text="🤖 ChatGPT", callback_data="service_chatgpt"),
        ],
        [
            InlineKeyboardButton(text="🎖️ Military", callback_data="service_military"),
        ],
        [
            InlineKeyboardButton(text="🔙 Kembali", callback_data="verify_now"),
            InlineKeyboardButton(text="🏠 Menu Utama", callback_data="menu_home"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_home() -> InlineKeyboardMarkup:
    """Tombol kembali ke menu utama - Desain Elegan"""
    keyboard = [[InlineKeyboardButton(text="🏠 Kembali ke Menu Utama", callback_data="menu_home")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_verify(service_name: str, cost: int) -> InlineKeyboardMarkup:
    """Tombol konfirmasi sebelum verifikasi - Desain Estetik"""
    keyboard = [
        [InlineKeyboardButton(text=f"✅ Proses Sekarang ({cost} Poin)", callback_data=f"start_{service_name}")],
        [InlineKeyboardButton(text="🔄 Ganti Layanan", callback_data="verify_now")],
        [InlineKeyboardButton(text="❌ Batalkan", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def profile_menu() -> InlineKeyboardMarkup:
    """Menu di dalam Profil - Desain Profesional"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Statistik Verifikasi", callback_data="stats")],
        [InlineKeyboardButton(text="📜 Riwayat Transaksi", callback_data="history_tx")],
        [InlineKeyboardButton(text="🏆 Prestasi & Ranking", callback_data="achievements")],
        [InlineKeyboardButton(text="⚙️ Pengaturan Akun", callback_data="settings")],
        [InlineKeyboardButton(text="🏠 Kembali", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def loading_animation() -> InlineKeyboardMarkup:
    """Keyboard animasi loading - Efek Visual"""
    keyboard = [
        [InlineKeyboardButton(text="⏳ Proses Sedang Berlangsung...", callback_data="loading")],
        [InlineKeyboardButton(text="🔄 Menyiapkan Data...", callback_data="loading")],
        [InlineKeyboardButton(text="⚡ Menghubungkan ke Server...", callback_data="loading")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def processing_animation() -> InlineKeyboardMarkup:
    """Keyboard animasi proses - Efek Visual"""
    keyboard = [
        [InlineKeyboardButton(text="📡 Mengirim Data...", callback_data="processing")],
        [InlineKeyboardButton(text="🔒 Verifikasi Identitas...", callback_data="processing")],
        [InlineKeyboardButton(text="✅ Menunggu Persetujuan...", callback_data="processing")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def success_animation() -> InlineKeyboardMarkup:
    """Keyboard animasi sukses - Efek Visual"""
    keyboard = [
        [InlineKeyboardButton(text="🎉 Verifikasi Berhasil!", callback_data="success")],
        [InlineKeyboardButton(text="✨ Selamat! Anda Disetujui", callback_data="success")],
        [InlineKeyboardButton(text="🏆 Status: Disetujui", callback_data="success")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def failure_animation() -> InlineKeyboardMarkup:
    """Keyboard animasi kegagalan - Efek Visual"""
    keyboard = [
        [InlineKeyboardButton(text="❌ Verifikasi Gagal", callback_data="failure")],
        [InlineKeyboardButton(text="⚠️ Silakan Coba Lagi", callback_data="failure")],
        [InlineKeyboardButton(text="🔄 Status: Gagal", callback_data="failure")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def cancel_verification() -> InlineKeyboardMarkup:
    """Tombol batalkan verifikasi - Desain Jelas"""
    keyboard = [
        [InlineKeyboardButton(text="❌ Batalkan Proses", callback_data="cancel_verify")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
