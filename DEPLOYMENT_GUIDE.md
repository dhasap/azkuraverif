# 🤖 Panduan Lengkap Deploy Bot AzkuraVerify

## Spesifikasi Minimum
- RAM: 1GB
- CPU: 1 Core
- OS: Ubuntu 22.04
- Metode: Python Virtual Environment (venv)

---

## 🛠️ Persiapan Awal (Hanya Sekali di Awal)

Sebelum deploy, siapkan VPS agar kuat menjalankan browser (Playwright) di RAM kecil.

### 1. Login ke VPS
```bash
ssh root@IP_VPS_ANDA
```

### 2. Update Sistem dan Install Dependencies
```bash
apt update && apt upgrade -y
apt install python3-pip python3-venv git screen curl wget -y
```

### 3. Buat SWAP Memory (Wajib untuk RAM 1GB)
Agar proses install tidak crash karena kehabisan RAM.
```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

Cek apakah SWAP aktif:
```bash
swapon --show
free -h
```

---

## 🚀 Cara Deploy (Instalasi Pertama)

### 1. Clone Repository
```bash
cd /home
git clone https://github.com/dhasap/azkuraverif.git
cd azkuraverif
```

### 2. Buat & Aktifkan Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```
(Pastikan muncul tanda `(venv)` di kiri terminal)

### 3. Install Library Python
```bash
pip install -r requirements.txt
```

### 4. Install Browser (Playwright)
```bash
playwright install-deps chromium
playwright install chromium
```

### 5. Setting Environment Variable (.env)
Buat file .env dan isi token bot Anda.
```bash
nano .env
```

Isi dengan:
```
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_IDS=123456789,987654321
TURSO_DATABASE_URL=turso_db_url
TURSO_AUTH_TOKEN=turso_auth_token
PERPLEXITY_PROXY=socks5://127.0.0.1:1080
```
(Simpan: Ctrl+X, lalu Y, lalu Enter)

### 6. Jalankan Bot (Background)
```bash
nohup ./venv/bin/python main.py > bot.log 2>&1 &
```

### 7. Cek Log (Memastikan jalan)
```bash
tail -f bot.log
```
(Tekan Ctrl+C untuk keluar)

---

## 🔄 Cara Redeploy (Update Kode)

Lakukan ini setiap kali ada update/perbaikan kode dari GitHub.

### 1. Masuk Folder Bot
```bash
cd /home/azkuraverif
```

### 2. Matikan Bot Lama
```bash
sudo pkill -9 -f "python main.py"
```

### 3. Tarik Update Terbaru
```bash
git pull origin main
```
(Jika ada error local changes, jalankan `git reset --hard` lalu pull lagi)

### 4. Update Library (Wajib jika requirements.txt berubah)
```bash
# Aktifkan venv dulu (jika belum)
source venv/bin/activate

pip install -r requirements.txt

# Cek update browser (opsional tapi disarankan)
playwright install-deps chromium
playwright install chromium
```

### 5. Jalankan Ulang Bot
```bash
nohup ./venv/bin/python main.py > bot.log 2>&1 &
```

### 6. Cek Status
```bash
tail -f bot.log
```

---

## 🔍 Manage Bot Process

### Cek Service PID Bot
```bash
ps aux | grep main.py
```

### Matikan Bot dengan PID
```bash
pkill -f main.py
# Atau jika perlu secara paksa
kill -9 PID_BOT_NYA
```

---

## 💡 Tips Tambahan

- **Lupa command masuk folder?** Gunakan `cd /home/azkuraverif`
- **Bot mati sendiri?** Cek log error dengan `cat bot.log`. Biasanya karena RAM penuh (pastikan SWAP aktif)
- **Venv tidak aktif?** Selalu gunakan `./venv/bin/python` saat menjalankan perintah nohup agar aman meskipun venv belum di-activate

---

## 📝 PANDUAN MENJALANKAN PROXY BELANDA (SSH TUNNEL)

**Project:** Azkura Bot (Perplexity Support)  
**Metode:** SSH Dropbear (Direct Tunnel)

### 📌 1. Data Akun SSH (SSHOcean)
Simpan data ini baik-baik. Jika expired, buat baru di sshocean.com (Server Netherlands).
- Host: nl1.sshocean.site
- Username: sshocean-azkuraku
- Password: azkura123
- Port: 22 (Bisa juga coba 80 atau 443 jika 22 gagal)
- Expired: 11 Jan 2026

---

### 🚀 2. Cara Menyalakan Proxy (Setiap VPS Restart)

Lakukan langkah ini setiap kali Anda baru menyalakan VPS atau jika proxy mati.

#### A. Buka Screen Baru
Agar proxy tetap jalan walau terminal ditutup.
```bash
screen -S proxy-belanda
```

#### B. Jalankan Perintah SSH Tunnel
Ketik/Paste perintah ini di dalam screen:
```bash
ssh -D 1080 -N -p 22 sshocean-azkuraku@nl1.sshocean.site
```

#### C. Masukkan Password
- Ketik password: `azkura123`
- Tekan Enter.
- Tanda Berhasil: Kursor akan diam berkedip dan tidak kembali ke tulisan root@....

#### D. Keluar dari Screen (Detach)
Jangan tekan Ctrl+C! Lakukan ini agar proxy jalan di background:
1. Tekan tombol Ctrl + A (bersamaan).
2. Lepaskan kedua tombol.
3. Tekan tombol D.

---

### ✅ 3. Cara Cek Apakah Proxy Jalan

Pastikan koneksi sudah tembus ke Belanda sebelum menjalankan bot.
```bash
curl --socks5-hostname 127.0.0.1:1080 https://ipinfo.io/json
```

- **Sukses:** Jika muncul `"country": "NL"`.
- **Gagal:** Jika error Connection refused. Ulangi langkah nomor 2.

---

### 🤖 4. Cara Menjalankan Bot

Jika proxy sudah aman, jalankan bot seperti biasa.

```bash
# 1. Masuk folder
cd /home/azkuraverif

# 2. Aktifkan Venv
source venv/bin/activate

# 3. Jalankan Bot
python main.py
```

---

## 🛠️ Tips & Solusi Masalah

### Jika Proxy Mati / Error:
Cukup matikan screen lama dan ulangi langkah 2.
```bash
screen -X -S proxy-belanda quit
```
Lalu mulai lagi dari `screen -S proxy-belanda`.

### Jika Akun Expired:
Buat akun baru di SSHOcean -> Edit perintah di Langkah 2B dengan Username & Host baru.

### Config .env (Sekali saja):
Pastikan file .env selalu berisi:
```
PERPLEXITY_PROXY=socks5://127.0.0.1:1080
```

### Monitoring Bot:
Untuk memantau status bot secara berkala:
```bash
# Cek log terbaru
tail -f bot.log

# Cek penggunaan RAM
free -h

# Cek apakah bot masih jalan
ps aux | grep main.py
```

### Backup Konfigurasi:
Simpan salinan .env Anda di tempat aman untuk kebutuhan backup.