import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Bot Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Warning: BOT_TOKEN is not set in .env")

# Admin IDs (comma separated in .env)
# Example: ADMIN_IDS=12345678,87654321
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "0").split(",") if x.strip().isdigit()]

# --- Turso Database Configuration ---
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

# --- Proxy Configuration (For Perplexity) ---
PERPLEXITY_PROXY = os.getenv("PERPLEXITY_PROXY", "")

# --- Economy System ---
VERIFY_COST = 1         # Default cost per verification
CHECKIN_REWARD = 1      # Daily check-in reward
REFERRAL_REWARD = 2     # Reward for inviter
REGISTER_REWARD = 3     # Initial balance for new users

# --- Links & Support ---
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/azkuraairdrop")
SUPPORT_URL = os.getenv("SUPPORT_URL", "https://t.me/dhasap1220")
APP_NAME = "Azkura Verify Bot"

# --- Force Subscribe ---
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "@azkuraairdrop") 
FORCE_SUB_URL = CHANNEL_URL
FORCE_SUB_MESSAGE = (
    "⛔️ <b>AKSES DIKUNCI</b>\n"
    "━━━━━━━━━━━━━━━━\n"
    "Untuk menggunakan bot ini, Anda wajib bergabung ke channel resmi kami terlebih dahulu.\n\n"
    "1. Klik tombol <b>Join Channel</b> di bawah.\n"
    "2. Setelah join, klik <b>Cek Status</b>."
)

# --- System Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(BASE_DIR, "tmp")

# Ensure tmp dir exists
os.makedirs(TMP_DIR, exist_ok=True)
