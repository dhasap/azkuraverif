# 🎨 Template ID Card - Panduan Lengkap

## ❓ Apakah Harus Racik Sendiri Template?

**JAWABAN: YA, WAJIB! ⚠️**

Template ID Card yang disertakan adalah **CONTOH/SAMPLE** untuk referensi struktur saja. Anda **WAJIB** edit dan customize sesuai kebutuhan Anda sendiri.

### ⚠️ Template yang Disertakan:

- ⚠️ **ChatGPT K12**: Contoh template HTML - WAJIB EDIT
- ⚠️ **Gemini One**: Contoh template PDF - WAJIB EDIT
- ⚠️ **Spotify Student**: Contoh student card - WAJIB EDIT
- ⚠️ **Bolt.new Teacher**: Contoh teacher badge - WAJIB EDIT
- ⚠️ **YouTube Premium**: Contoh verification - WAJIB EDIT

**PENTING**: Ini adalah full source code yang dishare, bukan layanan siap pakai. Template pribadi/production TIDAK ikut dishare. Anda harus buat/customize sendiri!

---

## 🔧 Kenapa WAJIB Edit Template?

**WAJIB edit template karena:**
1. ❌ **Template default hanya CONTOH struktur**
2. ❌ **Nama school/district adalah placeholder dummy**
3. ❌ **Design dan branding harus disesuaikan dengan kebutuhan Anda**
4. ❌ **Tidak bisa langsung pakai untuk verifikasi real**
5. ✅ **Harus personalisasi sesuai institusi/use case Anda**

### Yang WAJIB Diganti:

- 🔴 **School/District Name** (contoh: "School District Portal" → nama real)
- 🔴 **Department/Division** (contoh: "Education - Teaching Staff" → dept real)
- 🔴 **Logo dan Branding** (tambah logo institusi Anda)
- 🔴 **Warna Theme** (sesuaikan dengan branding Anda)
- 🔴 **Layout dan Design** (customize sesuai kebutuhan)
- 🔴 **Text dan Label** (ganti semua placeholder text)

---

## 📂 Lokasi Template Files

```
msverif/
├── k12/
│   └── card-temp.html          ← ChatGPT K12 (HTML template)
├── one/
│   └── img_generator.py        ← Gemini One (Python code)
├── spotify/
│   └── img_generator.py        ← Spotify (Python code)
├── Boltnew/
│   └── img_generator.py        ← Bolt.new (Python code)
└── youtube/
    └── img_generator.py        ← YouTube (Python code)
```

---

## 🎨 Cara Edit Template HTML (ChatGPT K12)

### 1. Buka File Template

```bash
# Windows
notepad k12/card-temp.html

# Linux/Mac
nano k12/card-temp.html

# Atau gunakan VS Code
code k12/card-temp.html
```

### 2. Edit Warna

```html
<style>
    :root {
        /* EDIT WARNA DI SINI */
        --primary-blue: #0056b3;      /* Warna utama */
        --border-gray: #dee2e6;       /* Warna border */
        --bg-gray: #f8f9fa;           /* Warna background */
    }
</style>
```

**Contoh Ubah Warna:**
```css
/* Warna Biru Original */
--primary-blue: #0056b3;

/* Ganti ke Hijau */
--primary-blue: #059669;

/* Ganti ke Merah */
--primary-blue: #dc2626;

/* Ganti ke Ungu */
--primary-blue: #7c3aed;
```

### 3. Edit Text/Content

```html
<!-- Nama District/Sekolah -->
<div class="district-name">
    <div class="logo-placeholder"></div>
    <span>School District Portal</span>  <!-- EDIT INI -->
</div>

<!-- Title Badge -->
<div class="badge-title">EMPLOYEE ACCESS BADGE</div>  <!-- EDIT INI -->

<!-- Department -->
<div class="info-item">
    <span class="info-label">Department:</span>
    <span class="info-value">Education - Teaching Staff</span>  <!-- EDIT INI -->
</div>
```

### 4. Tambah Logo

```html
<!-- Tambah di dalam <div class="district-name"> -->
<div class="district-name">
    <!-- Logo sekolah -->
    <img src="data:image/png;base64,YOUR_BASE64_IMAGE" 
         alt="Logo" 
         style="width: 40px; height: 40px; margin-right: 10px;">
    <span>School District Portal</span>
</div>
```

**Cara Convert Image ke Base64:**
```bash
# Online tool: https://www.base64-image.de/
# Atau dengan Python:
import base64
with open("logo.png", "rb") as f:
    base64_string = base64.b64encode(f.read()).decode()
    print(base64_string)
```

### 5. Edit Font

```html
<style>
    body {
        /* Ganti font family */
        font-family: 'Segoe UI', Arial, sans-serif;  /* Original */
        
        /* Contoh font lain: */
        /* font-family: 'Roboto', sans-serif; */
        /* font-family: 'Open Sans', sans-serif; */
        /* font-family: 'Poppins', sans-serif; */
    }
</style>
```

---

## 💻 Cara Edit Template Python (Services Lain)

### Example: Edit Spotify Template

**File**: `spotify/img_generator.py`

```python
def generate_student_card_pdf(first_name: str, last_name: str, dob: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # === EDIT WARNA ===
    # Original Spotify Green
    primary_color = colors.HexColor("#1DB954")
    
    # Ganti warna lain:
    # primary_color = colors.HexColor("#3b82f6")  # Blue
    # primary_color = colors.HexColor("#ef4444")  # Red
    # primary_color = colors.HexColor("#8b5cf6")  # Purple

    # === EDIT HEADER ===
    c.setFillColor(primary_color)
    c.rect(0, height - 150, width, 150, fill=True, stroke=False)
    
    # Title text
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width/2, height - 90, "STUDENT ID CARD")  # EDIT TEXT
    
    # === EDIT INFO FIELDS ===
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 14)
    
    # Name
    c.drawString(100, height - 200, "Full Name:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(250, height - 200, f"{first_name} {last_name}")
    
    # Student ID
    c.setFont("Helvetica", 14)
    c.drawString(100, height - 230, "Student ID:")
    c.setFont("Helvetica-Bold", 14)
    student_id = f"STU{random.randint(100000, 999999)}"
    c.drawString(250, height - 230, student_id)
    
    # Date of Birth
    c.setFont("Helvetica", 14)
    c.drawString(100, height - 260, "Date of Birth:")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(250, height - 260, dob)
    
    # === TAMBAH LOGO ===
    # Uncomment dan edit path
    # c.drawImage("path/to/logo.png", 50, height - 130, width=80, height=80)
    
    # === TAMBAH BARCODE/QR ===
    # from reportlab.graphics.barcode import qr
    # qr_code = qr.QrCodeWidget(student_id)
    # bounds = qr_code.getBounds()
    # qr_width = bounds[2] - bounds[0]
    # qr_height = bounds[3] - bounds[1]
    # d = Drawing(100, 100, transform=[100./qr_width, 0, 0, 100./qr_height, 0, 0])
    # d.add(qr_code)
    # renderPDF.draw(d, c, width - 150, height - 400)

    c.save()
    return buffer.getvalue()
```

### Customize Position (X, Y Coordinates)

```python
# Coordinate system: (0, 0) adalah POJOK KIRI BAWAH
# X: kiri ke kanan (0 -> width)
# Y: bawah ke atas (0 -> height)

# Contoh posisi:
c.drawString(100, 700, "Text di kiri atas")
c.drawString(400, 400, "Text di tengah")
c.drawString(100, 100, "Text di kiri bawah")
```

### Customize Colors

```python
from reportlab.lib import colors

# Predefined colors
colors.red
colors.blue
colors.green
colors.black
colors.white

# Custom Hex colors
colors.HexColor("#3b82f6")  # Blue
colors.HexColor("#ef4444")  # Red
colors.HexColor("#10b981")  # Green
colors.HexColor("#8b5cf6")  # Purple
colors.HexColor("#f59e0b")  # Orange

# RGB colors
colors.Color(0.2, 0.4, 0.8)  # RGB (0-1 scale)
```

### Customize Fonts

```python
# Available fonts (no installation needed):
"Helvetica"           # Normal
"Helvetica-Bold"      # Bold
"Helvetica-Oblique"   # Italic
"Times-Roman"         # Times New Roman
"Times-Bold"
"Times-Italic"
"Courier"             # Monospace
"Courier-Bold"

# Font size
c.setFont("Helvetica-Bold", 24)  # Font name, size
```

---

## 🧪 Testing Template Changes

### 1. Edit Template

```bash
# Edit file template yang diinginkan
nano k12/card-temp.html
# atau
nano spotify/img_generator.py
```

### 2. Restart Aplikasi

**Jika Docker:**
```bash
docker-compose restart web
```

**Jika Manual:**
```bash
# Ctrl+C untuk stop
python app.py
```

### 3. Test Verification

1. Login ke aplikasi
2. Pergi ke `/verify`
3. Pilih service yang templatenya diubah
4. Submit verification
5. Check hasil di verification history
6. Download PDF/PNG untuk lihat template baru

### 4. Debug Jika Error

```bash
# Check logs
# Docker:
docker-compose logs -f web

# Manual:
# Error akan muncul di terminal
```

**Common Errors:**

1. **SyntaxError di HTML**: Check HTML tags tutup dengan benar
2. **Import Error**: Pastikan library installed (`pip install reportlab pillow`)
3. **File Not Found**: Check path file benar
4. **Invalid Color**: Check format hex color `#RRGGBB`

---

## 📸 Preview Template

### Generate Preview Tanpa Verifikasi

Buat script test untuk preview:

```python
# test_template.py
from k12.img_generator import generate_teacher_pdf

# Generate test PDF
pdf_bytes = generate_teacher_pdf("John", "Doe")

# Save to file
with open("test_output.pdf", "wb") as f:
    f.write(pdf_bytes)

print("✅ Test PDF created: test_output.pdf")
```

Run test:
```bash
python test_template.py
```

---

## 💡 Tips & Best Practices

### 1. Backup Original Template
```bash
cp k12/card-temp.html k12/card-temp.html.backup
```

### 2. Buat Template dari Scratch (Recommended)
- **Jangan hanya edit contoh**, buat design sendiri
- Research template ID card real dari institusi sejenis
- Design yang unik dan profesional
- Pastikan tidak menjiplak design pihak lain

### 3. Incremental Changes
- Edit sedikit-sedikit
- Test setiap perubahan
- Jangan edit banyak sekaligus

### 4. Keep Template Realistic
- Design harus terlihat profesional
- Gunakan branding yang konsisten
- Hindari design yang terlalu generic

### 5. Test Different Scenarios
- Test dengan nama panjang/pendek
- Test dengan berbagai kombinasi data
- Pastikan layout tidak rusak

### 6. Legal & Ethical
- **JANGAN** menjiplak template institusi real
- **JANGAN** gunakan logo/branding tanpa izin
- Buat design original Anda sendiri
- Gunakan dengan tanggung jawab

---

## ❗ Troubleshooting

### Template Tidak Berubah?

**Problem**: Edit template tapi hasil tetap sama

**Solution**:
```bash
# 1. Clear browser cache (Ctrl+Shift+R)
# 2. Restart aplikasi
# 3. Check file save sudah benar
# 4. Check error di logs
```

### PDF Kosong / Error?

**Problem**: PDF generate tapi kosong atau error

**Solution**:
```python
# Check di img_generator.py:
# 1. Pastikan c.save() dipanggil
# 2. Check coordinate tidak negatif
# 3. Check font exists
# 4. Debug dengan print statements
```

### HTML Template Tidak Render?

**Problem**: HTML template tidak convert ke PDF

**Solution**:
```bash
# 1. Check xhtml2pdf installed
pip install xhtml2pdf

# 2. Check HTML valid (no unclosed tags)
# 3. Check CSS inline, bukan external file
# 4. Remove JavaScript (not supported)
```

---

## 🎓 Advanced Customization

### Multi-Language Support

```python
# Tambah parameter language
def generate_card(first_name, last_name, language="en"):
    if language == "id":
        title = "KARTU IDENTITAS GURU"
        dept_label = "Departemen:"
    else:
        title = "TEACHER ID CARD"
        dept_label = "Department:"
    
    # Use in template
    c.drawString(x, y, title)
```

### Dynamic QR Code

```python
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF

# Generate QR code
qr_code = qr.QrCodeWidget(f"https://verify.app/{employee_id}")
d = Drawing(100, 100)
d.add(qr_code)

# Render to PDF
renderPDF.draw(d, c, x, y)
```

### Add Watermark

```python
# Watermark di background
c.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
c.setFont("Helvetica-Bold", 60)
c.saveState()
c.rotate(45)
c.drawString(100, -100, "CONFIDENTIAL")
c.restoreState()
```

---

## 📚 Resources

### Learn HTML/CSS
- [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTML)
- [W3Schools](https://www.w3schools.com/html/)

### Learn ReportLab
- [Official Docs](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [ReportLab Tutorial](https://realpython.com/creating-modifying-pdf/)

### Color Palette Tools
- [Coolors.co](https://coolors.co/)
- [Adobe Color](https://color.adobe.com/)

### Base64 Image Converter
- [Base64 Image](https://www.base64-image.de/)
- [Online Base64](https://www.base64encode.org/)

---

## 🎉 Kesimpulan

- ⚠️ Template yang disertakan adalah **CONTOH/SAMPLE** struktur saja
- ⚠️ **WAJIB EDIT** sebelum pakai untuk verifikasi
- ⚠️ **WAJIB GANTI** semua nama school/district/branding
- ✅ Customize design dengan HTML atau Python
- ✅ Test setiap perubahan sebelum production
- ✅ Buat template original sesuai kebutuhan Anda

**Template default TIDAK bisa langsung pakai! Harus customize dulu.** ⚠️

---

## ⚠️ DISCLAIMER PENTING

**Ini adalah full source code yang dishare untuk pembelajaran dan development.**

- Template yang disertakan HANYA sebagai **contoh struktur/cara kerja**
- Template pribadi/production yang sudah working **TIDAK** ikut dishare
- Anda bertanggung jawab penuh membuat template Anda sendiri
- Gunakan source code ini dengan bijak dan bertanggung jawab
- Patuhi semua terms of service dan hukum yang berlaku

**Kalau template pribadi ikut dishare, ya kacau dong wkwkwk** 😂

---

**Need help?** Check logs untuk debugging atau research cara membuat template profesional.
