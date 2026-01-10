# 🌐 AZKURA VERIFY - Telegram Bot for SheerID Verification

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Aiogram](https://img.shields.io/badge/aiogram-3.0+-red)

> **AZKURA VERIFY** - Telegram Bot untuk Automated Student & Teacher Verification melalui SheerID dengan sistem poin dan manajemen pengguna
>
> **Created by Azkura © 2025** | Platform verifikasi otomatis berbasis Telegram dengan teknologi terkini

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Supported Services](#-supported-services)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Admin Panel](#-admin-panel)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)

---

## 📋 Overview

Telegram bot berbasis Python aiogram untuk automasi verifikasi identitas student/teacher melalui SheerID. Sistem otomatis generate informasi identitas, membuat dokumen verifikasi, dan submit ke platform SheerID dengan sistem poin untuk manajemen penggunaan.

---

## 🎯 Supported Services

| Service | Type | Status | Cost | Description |
|---------|------|--------|------|-------------|
| **Spotify Premium** | Student | ✅ Active | 1 Point | Spotify Premium Student Discount |
| **YouTube Premium** | Student | ✅ Active | 1 Point | YouTube Premium Student Discount |
| **K12 Teacher** | Teacher | ✅ Active | 3 Points | ChatGPT K12 Teacher Verification |
| **Military / Veteran** | Military | ✅ Active | 3 Points | ChatGPT Military/Veteran Verification |
| **Google One/Bolt** | Teacher | ✅ Active | 2 Points | Google One/Bolt.new Teacher Verification |
| **Perplexity Pro** | Student | ✅ Active | 2 Points | Perplexity Pro Student Verification |

---

## ✨ Key Features

- 🤖 **Telegram Bot Interface**: Full-featured bot dengan menu interaktif
- 🔐 **Secure Authentication**: Session-based dengan database terenkripsi
- 🚀 **One-Click Verification**: Automated verification process dengan browser automation
- 💰 **Points System**: Daily check-in, referral rewards, redemption codes
- 👥 **User Management**: Complete profile management & verification history
- 🛡️ **Admin Dashboard**: Comprehensive admin panel dengan real-time statistics
- 📊 **Analytics**: Detailed verification stats dan success rate monitoring
- 📱 **Fully Integrated**: Seamless Telegram experience
- 🔄 **Auto Code Retrieval**: Bolt.new service mendapat verification code otomatis
- 🛡️ **Force Subscribe**: Fitur wajib join channel sebelum menggunakan bot

---

## 🛠️ Tech Stack

### Backend
- **Framework**: aiogram 3.0+ (Telegram Bot Framework)
- **Database**: Turso/LibSQL (SQLite-compatible distributed database)
- **Authentication**: Telegram user authentication
- **Browser Automation**: Playwright Chromium
- **HTTP Client**: httpx untuk async requests

### Document Processing
- **PDF Generation**: xhtml2pdf, reportlab
- **Image Processing**: Pillow (PIL)
- **Screenshot**: Playwright screenshot API

### DevOps
- **Containerization**: Docker + Docker Compose
- **Process Manager**: Supervisor (optional)
- **Reverse Proxy**: Nginx (optional)

---

## 🚀 Installation

### Method 1: Docker (Recommended)

**Prerequisites:**
- Docker Desktop (Windows/Mac) atau Docker Engine (Linux)
- Docker Compose V2

**Steps:**

```bash
# 1. Navigate ke project directory
cd azkuraverif

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env dengan text editor
notepad .env  # Windows
nano .env     # Linux/Mac

# Sesuaikan:
# - BOT_TOKEN (dari @BotFather)
# - TURSO_DATABASE_URL (URL database Turso)
# - TURSO_AUTH_TOKEN (token autentikasi Turso)
# - ADMIN_IDS (ID Telegram admin)

# 4. Build dan jalankan
docker-compose up -d --build

# 5. Akses bot di Telegram
# Cari bot Anda dan mulai chatting
```

**Docker Commands:**

```bash
# Lihat logs
docker-compose logs -f web

# Stop bot
docker-compose down

# Restart bot
docker-compose restart

# Rebuild setelah update
docker-compose up -d --build

# Lihat container status
docker-compose ps
```

---

### Method 2: Manual Installation

**Prerequisites:**
- Python 3.11+
- Turso database account

**Steps:**

```bash
# 1. Navigate ke project directory
cd azkuraverif

# 2. Buat virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install Playwright browsers
playwright install chromium

# 6. Copy dan edit .env file
cp .env.example .env
nano .env

# 7. Jalankan bot
python main.py
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Copy dari `.env.example` dan sesuaikan:

```env
# === BOT CONFIGURATION ===
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321

# === DATABASE CONFIGURATION ===
TURSO_DATABASE_URL=your_turso_database_url
TURSO_AUTH_TOKEN=your_turso_auth_token

# === PROXY CONFIGURATION (Optional) ===
PERPLEXITY_PROXY=proxy_url_if_needed

# === ECONOMY SYSTEM ===
VERIFY_COST=1
CHECKIN_REWARD=1
REFERRAL_REWARD=2
REGISTER_REWARD=3

# === LINKS & SUPPORT ===
CHANNEL_URL=https://t.me/azkuraairdrop
SUPPORT_URL=https://t.me/dhasap1220
FORCE_SUB_CHANNEL=@azkuraairdrop
```

### Database Setup

Database Turso/LibSQL dibuat otomatis saat bot pertama kali dijalankan. Pastikan:
1. Turso database URL dan token valid
2. Koneksi internet stabil
3. Hak akses database cukup

---

## 🔐 Admin Panel

### Cara Akses Admin

**Method 1: Auto Admin (Configured in .env)**

1. Set admin IDs di `.env`:
   ```env
   ADMIN_IDS=123456789,987654321
   ```

2. Gunakan bot sebagai admin
3. Akses perintah admin melalui menu bot

**Method 2: Manual via Database**

```sql
UPDATE users SET is_admin = 1 WHERE telegram_id = your_telegram_id;
```

### Fitur Admin Panel

1. **Dashboard Overview**
   - Total users, verifications, points distributed
   - Success rate statistics
   - System status monitoring
   - Recent verifications list

2. **User Management**
   - View all users dengan search
   - Block/unblock users
   - Manage user points balance
   - View user verification history
   - Delete users (dengan konfirmasi)

3. **Points & Rewards Configuration**
   - Set daily check-in points
   - Set referral/invite points
   - Set new user signup bonus

4. **Redemption Codes**
   - Generate new codes
   - Set point value per code
   - Set max uses (usage limit)
   - Set expiry date
   - View active/redeemed/expired codes

5. **Verification History**
   - View all verification attempts
   - Filter by user/service/status/date
   - Download verification documents
   - View detailed logs

6. **Broadcast System**
   - Send announcements to all users
   - View broadcast history
   - Delete old broadcasts

7. **Maintenance Mode**
   - Enable/disable bot maintenance
   - Allow access only to admins during maintenance

---

## 🚀 Deployment

### Production dengan Docker

```bash
# 1. Upload project ke server

# 2. Setup .env untuk production
cp .env.example .env
nano .env

# Edit:
BOT_TOKEN=your_production_bot_token
TURSO_DATABASE_URL=your_production_turso_url
TURSO_AUTH_TOKEN=your_production_turso_token
ADMIN_IDS=your_admin_telegram_ids

# 3. Build dan run
docker-compose up -d --build

# 4. Monitor bot
docker-compose logs -f web
```

---

## 🔧 Troubleshooting

### Bot Not Starting

```bash
# Check environment variables
echo $BOT_TOKEN

# Check logs
docker-compose logs web

# Test database connection
python -c "import libsql_experimental; conn = libsql_experimental.connect(database='your_url', auth_token='your_token'); print('Connected')"
```

### Playwright Browser Not Found

```bash
playwright install chromium
```

### Database Connection Error

```bash
# Check Turso credentials
echo $TURSO_DATABASE_URL
echo $TURSO_AUTH_TOKEN
```

### Bot Not Responding

```bash
# Check if bot token is valid
curl https://api.telegram.org/bot$BOT_TOKEN/getMe
```

### Points System Not Working

```bash
# Check database tables
# Ensure users table has balance column
```

---

## 📝 Project Structure

```
azkuraverif/
├── main.py                      # Main Telegram bot application
├── config.py                    # Configuration settings
├── database_turso.py            # Database operations
├── keyboards.py                 # Inline keyboard definitions
├── parse_veterans.py            # Veteran data parser
├── requirements.txt             # Dependencies
├── docker-compose.yml           # Docker config
├── Dockerfile                   # Docker image
├── .env                         # Environment variables
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
│
├── handlers/                    # Telegram bot handlers
│   ├── start.py                 # Start command handler
│   ├── user_actions.py          # User action handlers
│   ├── verification.py          # Verification process handlers
│   ├── admin.py                 # Admin command handlers
│   └── navigation.py            # Navigation handlers
│
├── middlewares/                 # Bot middlewares
│   └── forcesub.py              # Force subscribe middleware
│
├── services/                    # Verification services
│   ├── Boltnew/                 # Bolt.new verification service
│   ├── k12/                     # K12 teacher verification
│   ├── military/                # Military/veteran verification
│   ├── one/                     # Google One verification
│   ├── perplexity/              # Perplexity verification
│   ├── spotify/                 # Spotify verification
│   ├── utils/                   # Utility functions
│   └── youtube/                 # YouTube verification
│
├── data/                        # Data files
```

---

## 📄 License

This project is licensed under the MIT License.

---

## ⚠️ Disclaimer

This tool is for educational purposes only. Use responsibly and comply with all applicable terms of service and laws. The developer is not responsible for any misuse of this tool.

---

## 👤 Author

**Azkura**
Created: 2025

---

## 🎉 Credits

- aiogram framework
- Turso/LibSQL
- Playwright browser automation
- Open source community

---

**Made with ❤️ by Azkura © 2025**
