"""File Konfigurasi Global untuk Web App"""
import os
import secrets
from dotenv import load_dotenv

# Load file .env
load_dotenv()

# Konfigurasi Web App
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
APP_NAME = os.getenv("APP_NAME", "MSVERIFY")
APP_DESCRIPTION = "Professional Student & Teacher Verification Platform"
APP_URL = os.getenv("APP_URL", "http://localhost:5000")
COPYRIGHT_YEAR = "2025"
COPYRIGHT_OWNER = "Masanto"

# Konfigurasi Database MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "sheerid_verify")

# Konfigurasi poin
VERIFY_COST = 1  # Poin yang digunakan untuk verifikasi
CHECKIN_REWARD = 1  # Poin reward check-in
INVITE_REWARD = 2  # Poin reward undangan
REGISTER_REWARD = 1  # Poin reward registrasi

# Konfigurasi admin default (akan dibuat saat setup)
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@msverify.app")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "Pasardigital25")

# Link bantuan
HELP_URL = os.getenv("HELP_URL", "https://whatsapp.com/channel/0029VakVntuKgsNz5QgqU30C")
