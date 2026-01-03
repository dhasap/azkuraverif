"""Template Pesan"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Dapatkan pesan sambutan"""
    msg = (
        f"🎉 Selamat datang, {full_name}!\n"
        "Anda berhasil mendaftar, mendapat 1 poin.\n"
    )
    if invited_by:
        msg += "Terima kasih bergabung melalui link undangan, pengundang mendapat 2 poin.\n"

    msg += (
        "\nBot ini dapat menyelesaikan autentikasi SheerID secara otomatis.\n"
        "Mulai cepat:\n"
        "/about - Pelajari fungsi bot\n"
        "/balance - Lihat saldo poin\n"
        "/help - Lihat daftar perintah lengkap\n\n"
        "Dapatkan lebih banyak poin:\n"
        "/qd - Check-in harian\n"
        "/invite - Undang teman\n"
        f"Gabung channel: {CHANNEL_URL}"
    )
    return msg


def get_about_message() -> str:
    """Dapatkan pesan tentang"""
    return (
        "🤖 Bot Autentikasi Otomatis SheerID\n"
        "\n"
        "Pengenalan Fungsi:\n"
        "- Menyelesaikan autentikasi mahasiswa/guru SheerID secara otomatis\n"
        "- Mendukung autentikasi Gemini One Pro, ChatGPT Teacher K12, Spotify Student, YouTube Student, Bolt.new Teacher\n"
        "\n"
        "Cara Mendapat Poin:\n"
        "- Bonus 1 poin saat registrasi\n"
        "- Check-in harian +1 poin\n"
        "- Undang teman +2 poin/orang\n"
        "- Gunakan kode (sesuai aturan kode)\n"
        f"- Gabung channel: {CHANNEL_URL}\n"
        "\n"
        "Cara Menggunakan:\n"
        "1. Mulai autentikasi di web dan salin link verifikasi lengkap\n"
        "2. Kirim /verify, /verify2, /verify3, /verify4 atau /verify5 dengan link tersebut\n"
        "3. Tunggu proses dan lihat hasilnya\n"
        "4. Autentikasi Bolt.new akan otomatis mendapatkan kode, jika perlu query manual gunakan /getV4Code <verification_id>\n"
        "\n"
        "Untuk perintah lainnya kirim /help"
    )


def get_help_message(is_admin: bool = False) -> str:
    """Dapatkan pesan bantuan"""
    msg = (
        "📖 Bot Autentikasi Otomatis SheerID - Bantuan\n"
        "\n"
        "Perintah User:\n"
        "/start - Mulai gunakan (registrasi)\n"
        "/about - Pelajari fungsi bot\n"
        "/balance - Lihat saldo poin\n"
        "/qd - Check-in harian (+1 poin)\n"
        "/invite - Buat link undangan (+2 poin/orang)\n"
        "/use <kode> - Gunakan kode tukar poin\n"
        f"/verify <link> - Autentikasi Gemini One Pro (-{VERIFY_COST} poin)\n"
        f"/verify2 <link> - Autentikasi ChatGPT Teacher K12 (-{VERIFY_COST} poin)\n"
        f"/verify3 <link> - Autentikasi Spotify Student (-{VERIFY_COST} poin)\n"
        f"/verify4 <link> - Autentikasi Bolt.new Teacher (-{VERIFY_COST} poin)\n"
        f"/verify5 <link> - Autentikasi YouTube Student Premium (-{VERIFY_COST} poin)\n"
        "/getV4Code <verification_id> - Dapatkan kode autentikasi Bolt.new\n"
        "/help - Lihat info bantuan ini\n"
        f"Autentikasi gagal lihat: {HELP_NOTION_URL}\n"
    )

    if is_admin:
        msg += (
            "\nPerintah Admin:\n"
            "/addbalance <ID user> <poin> - Tambah poin user\n"
            "/block <ID user> - Blacklist user\n"
            "/white <ID user> - Hapus blacklist\n"
            "/blacklist - Lihat daftar blacklist\n"
            "/genkey <kode> <poin> [jumlah] [hari] - Generate kode\n"
            "/listkeys - Lihat daftar kode\n"
            "/broadcast <teks> - Kirim notif ke semua user\n"
        )

    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Dapatkan pesan poin tidak cukup"""
    return (
        f"Poin tidak cukup! Perlu {VERIFY_COST} poin, saat ini {current_balance} poin.\n\n"
        "Cara mendapat poin:\n"
        "- Check-in harian /qd\n"
        "- Undang teman /invite\n"
        "- Gunakan kode /use <kode>"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Dapatkan panduan penggunaan perintah verifikasi"""
    return (
        f"Cara pakai: {command} <link SheerID>\n\n"
        "Contoh:\n"
        f"{command} https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
        "Dapatkan link verifikasi:\n"
        f"1. Kunjungi halaman autentikasi {service_name}\n"
        "2. Mulai proses autentikasi\n"
        "3. Salin URL lengkap dari address bar browser\n"
        f"4. Gunakan perintah {command} untuk submit"
    )
