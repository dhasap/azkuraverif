# 🌐 MSVERIFY - Professional Verification Platform

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Flask](https://img.shields.io/badge/flask-3.0+-red)

> **MSVERIFY** - Modern Web Application untuk Automated Student & Teacher Verification dengan UI/UX Professional dan Dark Theme Modern
>
> **Created by Masanto © 2025** | Platform verifikasi otomatis dengan teknologi terkini

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Supported Services](#-supported-services)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Admin Panel](#-admin-panel)
- [Template Customization](#-template-customization)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)

---

## 📋 Overview

Platform berbasis Python Flask untuk automasi verifikasi identitas student/teacher melalui SheerID. Sistem otomatis generate informasi identitas, membuat dokumen verifikasi, dan submit ke platform SheerID.

---

## 🎯 Supported Services

| Service | Type | Status | Auto Code | Description |
|---------|------|--------|-----------|-------------|
| **Gemini One Pro** | Teacher | ✅ Active | ❌ | Google AI Studio Education Discount |
| **ChatGPT K12** | Teacher | ✅ Active | ❌ | OpenAI ChatGPT Education Discount |
| **Spotify Student** | Student | ✅ Active | ❌ | Spotify Premium Student Discount |
| **Bolt.new Teacher** | Teacher | ✅ Active | ✅ Yes | Bolt.new Pro Education (Auto retrieve code) |
| **YouTube Premium** | Student | ⚠️ Beta | ❌ | YouTube Premium Student Discount |

---

## ✨ Key Features

- 🎨 **Modern Dark Theme UI**: Purple gradient design dengan 3D effects menggunakan Three.js
- 🔐 **Secure Authentication**: Session-based dengan bcrypt password hashing
- 🚀 **One-Click Verification**: Automated verification process dengan browser automation
- 💰 **Points System**: Daily check-in, referral rewards, redemption codes
- 👥 **User Management**: Complete profile management & verification history
- 🛡️ **Admin Dashboard**: Comprehensive admin panel dengan real-time statistics
- 📊 **Analytics**: Detailed verification stats dan success rate monitoring
- 🌐 **RESTful API**: Clean API architecture untuk extensibility
- 📱 **Fully Responsive**: Perfect display di semua devices (mobile, tablet, desktop)
- 🔄 **Auto Code Retrieval**: Bolt.new service mendapat verification code otomatis

---

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0+ (Python web framework)
- **Database**: MySQL 5.7+ / MariaDB
- **Authentication**: Werkzeug security + Flask sessions
- **Browser Automation**: Playwright Chromium
- **HTTP Client**: httpx untuk async requests

### Frontend
- **UI Framework**: Bootstrap 5.3
- **Icons**: Bootstrap Icons 1.11
- **3D Background**: Three.js particles animation
- **Styling**: Custom CSS dengan CSS Variables (dark theme)
- **JavaScript**: Vanilla JS + jQuery

### Document Processing
- **PDF Generation**: xhtml2pdf, reportlab
- **Image Processing**: Pillow (PIL)
- **Screenshot**: Playwright screenshot API

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Gunicorn (production)
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
cd msverif

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env dengan text editor
notepad .env  # Windows
nano .env     # Linux/Mac

# Sesuaikan:
# - SECRET_KEY (generate random string)
# - MYSQL_PASSWORD (strong password)
# - DEFAULT_ADMIN_EMAIL (email admin)

# 4. Build dan jalankan
docker-compose up -d --build

# 5. Akses aplikasi
# http://localhost:6969
```

**Docker Commands:**

```bash
# Lihat logs
docker-compose logs -f web

# Stop aplikasi
docker-compose down

# Restart aplikasi
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
- MySQL 5.7+ atau MariaDB 10.3+

**Steps:**

```bash
# 1. Navigate ke project directory
cd msverif

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

# 6. Setup MySQL database
mysql -u root -p
```

```sql
CREATE DATABASE sheerid_verify CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sheerid_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON sheerid_verify.* TO 'sheerid_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

```bash
# 7. Copy dan edit .env file
cp .env.example .env
nano .env

# 8. Jalankan aplikasi
python app.py

# Aplikasi running di: http://localhost:6969
```

**Production Mode (Gunicorn):**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## ⚙️ Configuration

### Environment Variables (.env)

Copy dari `.env.example` dan sesuaikan:

```env
# === APPLICATION ===
APP_NAME=MSVERIFY
APP_URL=http://localhost:6969
SECRET_KEY=generate-random-string-here-32-chars
FLASK_ENV=development

# === DATABASE ===
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=sheerid_user
MYSQL_PASSWORD=your_strong_password
MYSQL_DATABASE=sheerid_verify

# === DEFAULT ADMIN ===
# User yang register dengan email ini otomatis jadi admin
DEFAULT_ADMIN_EMAIL=admin@msverify.local
DEFAULT_ADMIN_PASSWORD=admin123456

# === POINTS SYSTEM ===
CHECKIN_POINTS=10
INVITE_POINTS=50
SIGNUP_POINTS=100

# === SUPPORT ===
HELP_URL=https://wa.me/your-whatsapp-number
```

### Generate Secret Key

```python
import secrets
print(secrets.token_hex(32))
# Output: 8f42a73054b1749f8f58848be5e6502c02c1e29f18b147b7a5c3d9e6f4b2a1c7
```

### Database Auto-Initialize

Database tables dibuat otomatis saat aplikasi pertama kali dijalankan. Pastikan:
1. MySQL server running
2. Database sudah dibuat
3. User punya privileges yang cukup

---

## 🔐 Admin Panel

### Cara Login Admin

**Method 1: Auto Admin (Recommended)**

1. Set email admin di `.env`:
   ```env
   DEFAULT_ADMIN_EMAIL=admin@msverify.local
   ```

2. Register akun baru dengan email tersebut

3. Akun otomatis menjadi admin

4. Login dan akses: `http://localhost:5000/admin`

**Method 2: Manual via Database**

```sql
UPDATE users SET is_admin = 1 WHERE email = 'your@email.com';
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

---

## 🎨 Template Customization

### ⚠️ WAJIB EDIT TEMPLATE SEBELUM PAKAI!

**PENTING**: Template yang disertakan adalah **CONTOH/SAMPLE** saja untuk referensi struktur. 

**ANDA WAJIB EDIT DAN CUSTOMIZE:**
- ❌ **JANGAN** langsung pakai template default
- ✅ **WAJIB** ganti nama school/district dengan milik Anda
- ✅ **WAJIB** customize design, warna, layout
- ✅ **WAJIB** sesuaikan dengan kebutuhan verifikasi Anda

**Ini adalah full source code yang dishare, bukan layanan siap pakai. Template pribadi TIDAK disertakan.**

---

### 🔥 WORKFLOW WAJIB SEBELUM EDIT TEMPLATE!

**LANGKAH PENTING - JANGAN SKIP!**

#### **Step 1: Testing Manual Dulu (WAJIB)**

Sebelum edit template di aplikasi ini, **WAJIB testing manual terlebih dahulu**:

1. **Buat ID Card Sendiri**
   - Racik ID card/dokumen Anda sendiri di luar aplikasi ini
   - Gunakan Photoshop, Canva, atau tools design lainnya
   - Buat design yang realistis dan profesional

2. **Testing dengan SheerID Manual**
   - Upload ID card racikan Anda ke SheerID secara manual
   - Test di platform asli (bukan aplikasi ini)
   - Coba submit verification manual dulu

3. **Pastikan BERHASIL Terlebih Dahulu**
   - ✅ ID card harus **APPROVED** oleh SheerID
   - ✅ Verification harus **SUCCESS** 100%
   - ✅ Tidak ada rejection atau masalah
   - ❌ Jika ditolak/gagal, **JANGAN** lanjut ke aplikasi ini

4. **Catat School/District yang Approved**
   - Simpan nama school/district yang berhasil
   - Catat semua detail yang di-approve
   - Gunakan yang sama untuk template di aplikasi ini

#### **Step 2: Edit Template di Aplikasi Ini**

**HANYA setelah testing manual BERHASIL**, baru edit template di aplikasi:

```bash
# 1. Buka file template
notepad k12/card-temp.html

# 2. GANTI dengan school/district yang SUDAH TERBUKTI BERHASIL
# - Gunakan nama PERSIS seperti yang di-approve
# - Copy design yang sudah berhasil
# - Sesuaikan warna dan layout yang sama

# 3. Testing di aplikasi
python app.py
```

#### **Step 3: Gunakan School yang Sudah Approved**

**WAJIB:**
- ✅ Gunakan **school/district yang sudah terbukti approved**
- ✅ Jangan coba-coba dengan random school
- ✅ Pakai nama dan detail yang persis sama
- ✅ Replicate design yang sudah berhasil

**JANGAN:**
- ❌ Langsung edit template tanpa testing manual
- ❌ Pakai school/district random yang belum di-test
- ❌ Asal ganti-ganti nama tanpa verifikasi
- ❌ Skip proses testing manual

---

### 🎯 Kenapa Harus Testing Manual Dulu?

1. **Menghindari Rejection**: SheerID bisa detect pattern. Testing manual lebih aman.
2. **Verifikasi Design**: Pastikan design Anda memang diterima sebelum automasi.
3. **Hemat Waktu**: Jangan buang waktu debug aplikasi untuk template yang memang ditolak.
4. **Success Rate Tinggi**: Template yang sudah proven berhasil = automasi lebih smooth.

**INGAT**: Aplikasi ini hanya AUTOMASI. Kualitas verifikasi tergantung TEMPLATE Anda!

---

### Lokasi Template

```
msverif/
├── k12/card-temp.html          # ChatGPT K12 (HTML) - SAMPLE
├── one/img_generator.py        # Gemini One (Python) - SAMPLE
├── spotify/img_generator.py    # Spotify (Python) - SAMPLE
├── Boltnew/img_generator.py    # Bolt.new (Python) - SAMPLE
└── youtube/img_generator.py    # YouTube (Python) - SAMPLE
```

### WAJIB Edit Template HTML (k12/card-temp.html)

```bash
# 1. Buka file
notepad k12/card-temp.html

# 2. WAJIB GANTI:
# - Nama School District (contoh: "School District Portal")
# - Department name (contoh: "Education - Teaching Staff")
# - Warna theme (--primary-blue, --border-gray, dll)
# - Layout dan design sesuai kebutuhan
# - Logo sekolah/institusi Anda

# 3. Edit CSS untuk personalisasi:
:root {
    --primary-blue: #0056b3;    /* Ganti warna */
    --border-gray: #dee2e6;     /* Ganti border */
    --bg-gray: #f8f9fa;         /* Ganti background */
}

# 4. Save dan restart aplikasi
docker-compose restart web
```

### WAJIB Edit Template Python (Services Lain)

```python
# File: spotify/img_generator.py

# WAJIB GANTI semua text, warna, dan branding
primary_color = colors.HexColor("#1DB954")  # Ganti warna
c.drawString(100, 700, "STUDENT ID CARD")   # Ganti text
c.setFont("Helvetica-Bold", 16)             # Sesuaikan font

# Tambah logo/branding Anda sendiri
# c.drawImage("your_logo.png", x, y, width, height)
```

### 💡 Tips Membuat Template yang Berhasil

**Berdasarkan Testing Manual Anda:**

1. **School/District yang Proven Works**
   - Gunakan school yang **sudah Anda test dan approved**
   - Jangan ganti-ganti school setelah berhasil
   - Catat semua detail yang membuat verification success

2. **Design Consistency**
   - Replicate **persis** design yang berhasil di testing manual
   - Gunakan warna, font, layout yang sama
   - Jangan ubah elemen yang sudah proven works

3. **Quality Matters**
   - Image resolution tinggi (minimal 1200x800px)
   - Text harus clear dan terbaca
   - Logo dan branding professional

4. **Data Realistis**
   - Nama harus masuk akal (first + last name)
   - ID numbers format realistic
   - Date format sesuai standar US

### ⚠️ Disclaimer Template

Template yang disertakan HANYA sebagai contoh struktur dan cara kerja system. Anda bertanggung jawab penuh untuk:

1. **Testing Manual Terlebih Dahulu**
   - WAJIB test ID card racikan Anda secara manual
   - Pastikan APPROVED sebelum implement di aplikasi
   - Gunakan school/district yang sudah terbukti berhasil

2. **Legal & Compliance**
   - Membuat template yang sesuai dengan kebutuhan Anda
   - Memastikan template tidak melanggar hak cipta pihak lain
   - Menyesuaikan design dengan institusi/kebutuhan Anda
   - Bertanggung jawab penuh atas penggunaan aplikasi

3. **Success Rate**
   - Kualitas template = kualitas verification
   - Aplikasi hanya AUTOMASI, bukan magic
   - Template yang proven works = success rate tinggi

**Lihat TEMPLATE_GUIDE.md untuk panduan lengkap customization**

---

### 🚨 PERINGATAN PENTING

**JANGAN:**
- ❌ Langsung pakai template default tanpa edit
- ❌ Skip proses testing manual
- ❌ Gunakan school random yang belum di-test
- ❌ Expect aplikasi bekerja dengan template asal-asalan

**LAKUKAN:**
- ✅ Testing manual dulu sampai APPROVED
- ✅ Catat school/district yang berhasil
- ✅ Edit template dengan detail yang sudah proven
- ✅ Maintain consistency dengan yang berhasil

**Remember**: Ini tool AUTOMASI. Anda yang bertanggung jawab untuk template quality!

---

## 📡 API Documentation

### Authentication Endpoints

```http
POST /register
POST /login
POST /logout
```

### User Endpoints

```http
GET  /api/user/profile
POST /api/checkin
POST /api/redeem
```

### Verification Endpoints

```http
POST /api/verify
{
    "service": "gemini_one|chatgpt_k12|spotify|boltnew|youtube",
    "url": "https://services.sheerid.com/verify/..."
}
```

### Admin Endpoints

```http
GET  /api/admin/users
GET  /api/admin/stats
GET  /api/admin/codes
POST /api/admin/codes/create
GET  /api/admin/verifications
```

**Response Format:**

```json
{
    "success": true,
    "message": "Operation successful",
    "data": { }
}
```

---

## 🚀 Deployment

### Production dengan Docker

```bash
# 1. Upload project ke server

# 2. Setup .env untuk production
cp .env.example .env
nano .env

# Edit:
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
APP_URL=https://yourdomain.com
MYSQL_PASSWORD=<strong-password>

# 3. Build dan run
docker-compose up -d --build

# 4. Setup Nginx (optional)
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🔧 Troubleshooting

### Database Connection Error

```bash
# Check MySQL running
sudo systemctl status mysql
sudo systemctl start mysql

# Test connection
mysql -u sheerid_user -p sheerid_verify
```

### Playwright Browser Not Found

```bash
playwright install chromium
```

### Port Already in Use

```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### CSS/JS Not Loading

```bash
# Clear browser cache: Ctrl+Shift+R

# Restart aplikasi
docker-compose restart web
```

### Template Not Found

```bash
# Check file exists
ls -la k12/card-temp.html

# Restore dari backup jika hilang
```

---

## 📝 Project Structure

```
msverif/
├── app.py                      # Main Flask application
├── api_verify.py               # Verification API routes
├── api_admin.py                # Admin API routes
├── config.py                   # Configuration
├── database_mysql.py           # Database operations
├── requirements.txt            # Dependencies
├── docker-compose.yml          # Docker config
├── Dockerfile                  # Docker image
├── .env                        # Environment variables
├── README.md                   # This file
├── TEMPLATE_GUIDE.md           # Template customization guide
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── verify.html
│   └── admin.html
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   └── js/
│       └── main.js            # Main JavaScript
│
├── utils/                      # Utilities
│   ├── checks.py              # Validation
│   ├── concurrency.py         # Rate limiting
│   └── messages.py            # Flash messages
│
├── k12/                        # ChatGPT K12 service
│   ├── img_generator.py
│   ├── name_generator.py
│   ├── sheerid_verifier.py
│   └── card-temp.html
│
├── one/                        # Gemini One service
├── spotify/                    # Spotify service
├── Boltnew/                    # Bolt.new service
├── youtube/                    # YouTube service
│
└── logs/                       # Application logs
```

---

## 📄 License

This project is licensed under the MIT License.

---

## ⚠️ Disclaimer

This tool is for educational purposes only. Use responsibly and comply with all applicable terms of service and laws.

---

## 👤 Author

**Masanto**  
Created: 2025

---

## 🎉 Credits

- Flask framework
- Bootstrap 5
- Playwright browser automation
- Three.js for 3D effects
- Open source community

---

**Made with ❤️ by Masanto © 2025**
