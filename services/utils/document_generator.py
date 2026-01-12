"""
Modul untuk menghasilkan dokumen verifikasi dalam bentuk gambar
Menggunakan PIL untuk membuat dokumen yang diadaptasi dari template-template di azkuraidgen
"""
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import hashlib
from functools import wraps
from .data_generator import (
    generate_random_data,
    generate_teacher_data,
    generate_admission_letter_data,
    generate_enrollment_certificate_data,
    generate_schedule_data,
    generate_employment_letter_data,
    generate_salary_statement_data,
    generate_teaching_certificate_data
)


def cached_document_creation(func):
    """
    Decorator to cache document creation results.
    Currently implemented as a pass-through to fix NameError.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@cached_document_creation
def create_transcript_document(data=None, width=800, height=1000):
    """
    Membuat dokumen transkrip nilai dalam bentuk gambar
    Berdasarkan TranscriptTemplate.jsx
    """
    if data is None:
        data = generate_random_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font
    try:
        title_font = ImageFont.truetype("times.ttf", 24)
        header_font = ImageFont.truetype("times.ttf", 20)
        regular_font = ImageFont.truetype("times.ttf", 16)
        bold_font = ImageFont.truetype("times.ttf", 16)
        small_font = ImageFont.truetype("times.ttf", 14)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header
    y_offset = 40
    draw.text((40, y_offset), data["university_name"], fill=(80, 33, 47), font=title_font)
    y_offset += 30
    draw.text((40, y_offset), "Office of the University Registrar", fill=(0, 0, 0), font=header_font)
    y_offset += 25
    draw.text((40, y_offset), "Academic Transcript", fill=(0, 0, 0), font=regular_font)
    y_offset += 30
    
    # Student Information
    draw.rectangle([(40, y_offset), (width-40, y_offset+100)], outline=(204, 204, 204), width=1)
    
    info_y = y_offset + 10
    draw.text((50, info_y), "Name:", fill=(0, 0, 0), font=bold_font)
    draw.text((150, info_y), data["student_name"], fill=(0, 0, 0), font=regular_font)
    
    info_y += 20
    draw.text((50, info_y), "Student ID:", fill=(0, 0, 0), font=bold_font)
    draw.text((150, info_y), data["student_id"], fill=(0, 0, 0), font=regular_font)
    
    info_y += 20
    draw.text((400, info_y), "Date Issued:", fill=(0, 0, 0), font=bold_font)
    draw.text((520, info_y), data["issue_date"], fill=(0, 0, 0), font=regular_font)
    
    info_y += 20
    draw.text((400, info_y), "Program:", fill=(0, 0, 0), font=bold_font)
    draw.text((520, info_y), data["program"], fill=(0, 0, 0), font=regular_font)
    
    info_y += 20
    draw.text((50, info_y), "College:", fill=(0, 0, 0), font=bold_font)
    draw.text((150, info_y), data["college"], fill=(0, 0, 0), font=regular_font)
    
    info_y += 20
    draw.text((400, info_y), "Major:", fill=(0, 0, 0), font=bold_font)
    draw.text((520, info_y), data["major"], fill=(0, 0, 0), font=regular_font)
    
    y_offset = info_y + 30
    
    # Current Term Header
    draw.rectangle([(40, y_offset), (width-40, y_offset+30)], fill=(224, 224, 224))
    draw.text((50, y_offset+5), data["term"], fill=(0, 0, 0), font=bold_font)
    y_offset += 40
    
    # Course Headers
    draw.rectangle([(40, y_offset), (width-40, y_offset+30)], fill=(242, 242, 242))
    headers = ["Course", "Description", "Grade", "Hours", "Quality Pts"]
    x_positions = [50, 200, 450, 550, 650]
    
    for i, header in enumerate(headers):
        draw.text((x_positions[i], y_offset+5), header, fill=(0, 0, 0), font=bold_font)
    
    y_offset += 30
    
    # Course Rows
    for course in data["courses"]["current"]:
        draw.line([(40, y_offset), (width-40, y_offset)], fill=(221, 221, 221), width=1)
        draw.text((x_positions[0], y_offset+5), course["code"], fill=(0, 0, 0), font=regular_font)
        draw.text((x_positions[1], y_offset+5), course["name"], fill=(0, 0, 0), font=regular_font)
        draw.text((x_positions[2], y_offset+5), course["grade"], fill=(0, 0, 0), font=regular_font)
        draw.text((x_positions[3], y_offset+5), str(course["hours"]), fill=(0, 0, 0), font=regular_font)
        draw.text((x_positions[4], y_offset+5), str(course["quality_points"]), fill=(0, 0, 0), font=regular_font)
        y_offset += 30
    
    # Term Stats
    stats = data["stats"]["current"]
    draw.text((50, y_offset+10), f"Term Totals:", fill=(0, 0, 0), font=bold_font)
    draw.text((180, y_offset+10), f"Attempted: {stats['attempted']:.2f}", fill=(0, 0, 0), font=regular_font)
    draw.text((320, y_offset+10), f"Earned: {stats['earned']:.2f}", fill=(0, 0, 0), font=regular_font)
    draw.text((420, y_offset+10), f"GPA Hours: {stats['attempted']:.2f}", fill=(0, 0, 0), font=regular_font)
    draw.text((550, y_offset+10), f"Quality Points: {stats['quality_points']:.2f}", fill=(0, 0, 0), font=regular_font)
    draw.text((720, y_offset+10), f"Term GPA: {stats['gpa']}", fill=(0, 0, 0), font=bold_font)
    y_offset += 50
    
    # Next Term Header
    draw.rectangle([(40, y_offset), (width-40, y_offset+30)], fill=(224, 224, 224))
    draw.text((50, y_offset+5), "Spring 2025", fill=(0, 0, 0), font=bold_font)
    y_offset += 40
    
    # Next Term Course Headers
    draw.rectangle([(40, y_offset), (width-40, y_offset+30)], fill=(242, 242, 242))
    for i, header in enumerate(headers):
        draw.text((x_positions[i], y_offset+5), header, fill=(0, 0, 0), font=bold_font)
    
    y_offset += 30
    
    # Next Term Course Rows
    for course in data["courses"]["next"]:
        draw.line([(40, y_offset), (width-40, y_offset)], fill=(221, 221, 221), width=1)
        draw.text((x_positions[0], y_offset+5), course["code"], fill=(0, 0, 0), font=regular_font)
        draw.text((x_positions[1], y_offset+5), course["name"], fill=(0, 0, 0), font=regular_font)
        draw.text((x_positions[2], y_offset+5), course["grade"], fill=(0, 0, 0), font=regular_font)
        draw.text((x_positions[3], y_offset+5), str(course["hours"]), fill=(0, 0, 0), font=regular_font)
        draw.text((x_positions[4], y_offset+5), str(course["quality_points"]), fill=(0, 0, 0), font=regular_font)
        y_offset += 30
    
    # Next Term Stats
    stats_next = data["stats"]["next"]
    draw.text((50, y_offset+10), f"Term Totals:", fill=(0, 0, 0), font=bold_font)
    draw.text((180, y_offset+10), f"Attempted: {stats_next['attempted']:.2f}", fill=(0, 0, 0), font=regular_font)
    draw.text((320, y_offset+10), f"Earned: {stats_next['earned']:.2f}", fill=(0, 0, 0), font=regular_font)
    draw.text((420, y_offset+10), f"GPA Hours: {stats_next['attempted']:.2f}", fill=(0, 0, 0), font=regular_font)
    draw.text((550, y_offset+10), f"Quality Points: {stats_next['quality_points']:.2f}", fill=(0, 0, 0), font=regular_font)
    draw.text((720, y_offset+10), f"Term GPA: {stats_next['gpa']}", fill=(0, 0, 0), font=bold_font)
    y_offset += 50
    
    # Cumulative Stats
    draw.line([(40, y_offset), (width-40, y_offset)], fill=(51, 51, 51), width=2)
    y_offset += 10
    
    stats_cum = data["stats"]["cumulative"]
    draw.text((50, y_offset), f"Cumulative Totals:", fill=(0, 0, 0), font=bold_font)
    draw.text((200, y_offset), f"Attempted: {stats_cum['attempted']}", fill=(0, 0, 0), font=regular_font)
    draw.text((350, y_offset), f"Earned: {stats_cum['earned']}", fill=(0, 0, 0), font=regular_font)
    draw.text((480, y_offset), f"GPA Hours: {stats_cum['attempted']}", fill=(0, 0, 0), font=regular_font)
    draw.text((620, y_offset), f"Quality Points: {stats_cum['quality_points']}", fill=(0, 0, 0), font=regular_font)
    draw.text((750, y_offset), f"Cumulative GPA: {stats_cum['gpa']}", fill=(0, 0, 0), font=bold_font)
    
    y_offset += 20
    draw.text((50, y_offset), f"Academic Standing:", fill=(0, 0, 0), font=bold_font)
    draw.text((200, y_offset), "Good Standing", fill=(0, 0, 0), font=regular_font)
    
    # Footer
    y_offset += 50
    draw.text((width//2 - 100, y_offset), "*** END OF TRANSCRIPT ***", fill=(102, 102, 102), font=small_font)
    
    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


@cached_document_creation
def create_tuition_document(data=None, width=800, height=1000):
    """
    Membuat dokumen tuition statement dalam bentuk gambar
    Berdasarkan TuitionTemplate.jsx
    """
    if data is None:
        data = generate_random_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font
    try:
        title_font = ImageFont.truetype("arial.ttf", 26)
        subtitle_font = ImageFont.truetype("arial.ttf", 14)
        regular_font = ImageFont.truetype("arial.ttf", 16)
        bold_font = ImageFont.load_default()
        small_font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header
    y_offset = 40
    draw.rectangle([(0, 0), (width, 60)], fill=(80, 33, 47))
    draw.text((40, 15), data["university_name"], fill=(255, 255, 255), font=title_font)
    draw.text((40, 45), "Student Business Services", fill=(255, 255, 255), font=subtitle_font)
    
    # Account Statement Title
    draw.text((width - 200, 15), "ACCOUNT STATEMENT", fill=(0, 0, 0), font=bold_font)
    draw.text((width - 200, 35), f"Statement Date: {data['statement_date']}", fill=(0, 0, 0), font=regular_font)
    draw.text((width - 200, 55), f"Payment Due Date: {data['due_date']}", fill=(0, 0, 0), font=regular_font)
    
    y_offset = 90
    
    # Student Info
    draw.text((40, y_offset), "To:", fill=(0, 0, 0), font=bold_font)
    draw.text((100, y_offset), data["student_name"], fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((100, y_offset), data["address"], fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((40, y_offset), "Student ID:", fill=(0, 0, 0), font=bold_font)
    draw.text((150, y_offset), data["student_id"], fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((40, y_offset), "Term:", fill=(0, 0, 0), font=bold_font)
    draw.text((100, y_offset), data["term"], fill=(0, 0, 0), font=regular_font)
    
    y_offset += 40
    
    # Table Headers
    draw.rectangle([(40, y_offset), (width-40, y_offset+30)], fill=(242, 242, 242))
    draw.line([(40, y_offset), (width-40, y_offset)], fill=(222, 226, 230), width=2)
    draw.line([(40, y_offset+30), (width-40, y_offset+30)], fill=(222, 226, 230), width=2)
    
    draw.text((50, y_offset+8), "Description", fill=(0, 0, 0), font=bold_font)
    draw.text((width-100, y_offset+8), "Amount", fill=(0, 0, 0), font=bold_font)
    
    y_offset += 30
    
    # Table Rows
    charges = [
        ("Tuition - Undergraduate (Non-Resident) - 15 Hours", data["tuition"]["base"]),
        (f"Differential Tuition - {data['college']}", data["tuition"]["differential"]),
        ("Student Service Fee", "$340.00"),
        ("Computer Service Fee", "$210.00"),
        ("Library Fee", "$150.00"),
        ("Medical Fee", "$95.00"),
        ("Other Required University Fees", "$680.00"),
        ("International Student Operations Fee", "$75.00"),
        ("International Student Health Insurance", "$1,650.00")
    ]
    
    for desc, amount in charges:
        draw.line([(40, y_offset), (width-40, y_offset)], fill=(222, 226, 230), width=1)
        draw.text((50, y_offset+8), desc, fill=(0, 0, 0), font=regular_font)
        draw.text((width-100, y_offset+8), amount, fill=(0, 0, 0), font=regular_font)
        y_offset += 30
    
    # Summary Section
    y_offset += 20
    draw.line([(40, y_offset), (width-40, y_offset)], fill=(222, 226, 230), width=2)
    
    draw.text((width-200, y_offset+20), "Total Charges:", fill=(0, 0, 0), font=regular_font)
    draw.text((width-80, y_offset+20), data["tuition"]["total"], fill=(0, 0, 0), font=regular_font)
    
    y_offset += 25
    draw.text((width-350, y_offset), f"Payments/Credits (as of {data['statement_date']}):", fill=(0, 0, 0), font=regular_font)
    draw.text((width-80, y_offset), f"({data['tuition']['total']})", fill=(0, 0, 0), font=regular_font)
    
    y_offset += 25
    draw.line([(40, y_offset), (width-40, y_offset)], fill=(222, 226, 230), width=2)
    
    draw.text((width-200, y_offset+20), "BALANCE DUE:", fill=(80, 33, 47), font=bold_font)
    draw.text((width-80, y_offset+20), "$0.00", fill=(80, 33, 47), font=bold_font)
    
    # Footer
    y_offset += 60
    footer_text = "Thank you for your payment. This statement reflects account activity as of the date indicated. For questions, please contact Student Business Services."
    draw.text((40, y_offset), footer_text, fill=(108, 117, 125), font=small_font)
    
    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


@cached_document_creation
def create_student_id_front(data=None, width=750, height=480, custom_logo_path=None, custom_photo_path=None):
    """
    Membuat bagian depan kartu identitas pelajar dalam bentuk gambar
    Berdasarkan StudentCardFrontTemplate.jsx
    """
    if data is None:
        data = generate_random_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Font
    try:
        title_font_large = ImageFont.truetype("arial.ttf", 33)
        title_font_small = ImageFont.truetype("arial.ttf", 18)
        label_font = ImageFont.truetype("arial.ttf", 15)
        value_font = ImageFont.truetype("arial.ttf", 24)
        date_font = ImageFont.truetype("arial.ttf", 19)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font_large = ImageFont.load_default()
        title_font_small = ImageFont.load_default()
        label_font = ImageFont.load_default()
        value_font = ImageFont.load_default()
        date_font = ImageFont.load_default()

    # Header dengan warna khusus
    card_color = data.get("card_color", "#3b82f6")
    # Konversi warna hex ke RGB
    r = int(card_color[1:3], 16)
    g = int(card_color[3:5], 16)
    b = int(card_color[5:7], 16)

    draw.rectangle([(0, 0), (width, 135)], fill=(r, g, b))

    # Logo - jika path logo kustom disediakan, gunakan itu
    # Jika tidak, buat logo berbasis inisial yang terlihat resmi
    logo_x, logo_y = 30, 12
    logo_size = 112
    
    if custom_logo_path and os.path.exists(custom_logo_path):
        try:
            logo_img = Image.open(custom_logo_path).convert("RGBA")
            logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            mask = Image.new('L', (logo_size, logo_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, logo_size, logo_size), fill=255)
            img.paste(logo_img, (logo_x, logo_y), mask)
        except Exception:
            # Fallback ke generated logo jika gagal
            pass
    
    # GENERATED LOGO LOGIC (Selalu fallback ke sini jika tidak ada custom logo)
    if not (custom_logo_path and os.path.exists(custom_logo_path)):
        # Ambil inisial universitas (misal "Pennsylvania State University" -> "PSU")
        uni_name = data.get("university_name", "University")
        ignored_words = ["of", "the", "at", "and"]
        initials = "".join([word[0].upper() for word in uni_name.split() if word.lower() not in ignored_words])[:3]
        
        # Gambar lingkaran background logo (putih)
        draw.ellipse([(logo_x, logo_y), (logo_x + logo_size, logo_y + logo_size)], fill='white', outline='#e0e0e0', width=2)
        
        # Gambar inisial di tengah
        try:
            # Cari font tebal jika ada
            logo_font = ImageFont.truetype("arialbd.ttf", 40)
        except:
            try:
                logo_font = ImageFont.truetype("arial.ttf", 40)
            except:
                logo_font = ImageFont.load_default()
        
        # Warna teks inisial sesuai warna kartu
        draw.text((logo_x + logo_size//2, logo_y + logo_size//2), initials, fill=card_color, font=logo_font, anchor="mm")

    # Nama universitas dan subtitle
    draw.text((170, 25), data["university_name"], fill='white', font=title_font_large)
    draw.text((170, 65), data["card_subtitle"], fill=(255, 255, 255, 195), font=title_font_small)

    # Background body
    draw.rectangle([(0, 135), (width, 390)], fill=(250, 250, 250))

    # FOTO PELAJAR
    photo_x, photo_y = 30, 165
    photo_width, photo_height = 140, 180
    
    # 1. Cek apakah ada custom photo asli yang diupload
    photo_pasted = False
    if custom_photo_path and os.path.exists(custom_photo_path):
        try:
            student_photo = Image.open(custom_photo_path).convert("RGB")
            
            # Auto-crop dan resize agar pas 140x180 (maintain aspect ratio)
            photo_ratio = photo_width / photo_height
            img_ratio = student_photo.width / student_photo.height
            
            if img_ratio > photo_ratio:
                # Terlalu lebar, crop kiri-kanan
                new_width = int(student_photo.height * photo_ratio)
                left = (student_photo.width - new_width) / 2
                student_photo = student_photo.crop((left, 0, left + new_width, student_photo.height))
            else:
                # Terlalu tinggi, crop atas-bawah
                new_height = int(student_photo.width / photo_ratio)
                top = (student_photo.height - new_height) / 2
                student_photo = student_photo.crop((0, top, student_photo.width, top + new_height))
            
            student_photo = student_photo.resize((photo_width, photo_height), Image.Resampling.LANCZOS)
            img.paste(student_photo, (photo_x, photo_y))
            
            # Gambar bingkai tipis di atas foto
            draw.rectangle([(photo_x, photo_y), (photo_x + photo_width, photo_y + photo_height)], outline='#9ca3af', width=1)
            photo_pasted = True
        except Exception as e:
            pass

    # 2. Fallback ke SILUET jika tidak ada foto asli atau gagal
    if not photo_pasted:
        # Background foto abu-abu terang
        draw.rectangle([(photo_x, photo_y), (photo_x + photo_width, photo_y + photo_height)], fill='#d1d5db', outline='#9ca3af', width=2)
        
        # Gambar siluet orang (Kepala + Bahu)
        silhouette_color = '#6b7280'
        
        # Kepala
        head_radius = 35
        head_center_x = photo_x + photo_width // 2
        head_center_y = photo_y + 65
        draw.ellipse([(head_center_x - head_radius, head_center_y - head_radius), 
                      (head_center_x + head_radius, head_center_y + head_radius)], 
                     fill=silhouette_color)
        
        # Bahu
        shoulder_width = 100
        shoulder_height = 80
        shoulder_x1 = head_center_x - shoulder_width // 2
        draw.chord([(shoulder_x1, head_center_y + 40), 
                    (shoulder_x1 + shoulder_width, head_center_y + 40 + shoulder_height*2)], 
                   start=180, end=0, fill=silhouette_color)

    # Informasi pelajar
    info_x = photo_x + photo_width + 30
    info_y = photo_y + 10

    draw.text((info_x, info_y), "NAME", fill='#666', font=label_font)
    draw.text((info_x, info_y + 25), data["student_name"], fill='#333', font=value_font)

    info_y += 60
    draw.text((info_x, info_y), "STUDENT ID", fill='#666', font=label_font)
    draw.text((info_x, info_y + 25), data["student_id"], fill='#333', font=value_font)

    info_y += 60
    draw.text((info_x, info_y), "FACULTY", fill='#666', font=label_font)
    draw.text((info_x, info_y + 25), data["college"], fill='#333', font=value_font)

    # Footer
    draw.rectangle([(0, 390), (width, 480)], fill='white')
    draw.line([(0, 390), (width, 390)], fill='#e0e0e0', width=1)

    # Tanggal cetak dan tanggal berlaku
    date_x = 30
    date_y = 410
    draw.text((date_x, date_y), "ISSUE DATE", fill='#666', font=label_font)
    draw.text((date_x, date_y + 20), data["card_issue_date"], fill='#333', font=date_font)

    date_x = width - 150
    draw.text((date_x, date_y), "VALID UNTIL", fill='#666', font=label_font)
    draw.text((date_x, date_y + 20), data["card_valid_date"], fill='#333', font=date_font)

    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return img_buffer


@cached_document_creation
def create_student_id_back(data=None, width=750, height=480, custom_logo_path=None):
    """
    Membuat bagian belakang kartu identitas pelajar dalam bentuk gambar
    Berdasarkan StudentCardBackTemplate.jsx
    """
    if data is None:
        data = generate_random_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)

    # Font
    try:
        label_font = ImageFont.truetype("arial.ttf", 15)
        value_font = ImageFont.truetype("arial.ttf", 21)
        notice_font = ImageFont.truetype("arial.ttf", 16)
        signature_font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        label_font = ImageFont.load_default()
        value_font = ImageFont.load_default()
        notice_font = ImageFont.load_default()
        signature_font = ImageFont.load_default()

    # Hitam magnetic stripe
    draw.rectangle([(0, 0), (width, 75)], fill='#000')

    # Background putih untuk konten
    draw.rectangle([(0, 75), (width, height)], fill='white')

    # Alamat pemilik kartu
    addr_x, addr_y = 30, 90
    draw.text((addr_x, addr_y), "CARDHOLDER ADDRESS", fill='#666', font=label_font)
    draw.text((addr_x, addr_y + 25), data["address"], fill='#333', font=value_font)

    # Catatan
    notice_y = addr_y + 70
    draw.text((addr_x, notice_y), data["card_notice"], fill='#666', font=notice_font)

    # Tanda tangan dan logo
    signature_x = 30
    signature_y = height - 80
    draw.text((signature_x, signature_y), data["student_name"], fill='#333', font=signature_font)
    draw.text((signature_x, signature_y + 30), "Cardholder Signature", fill='#999', font=label_font)

    # Logo - jika path logo kustom disediakan, gunakan itu, jika tidak gunakan placeholder
    logo_x = width - 130
    logo_y = height - 130
    logo_size = 120
    if custom_logo_path and os.path.exists(custom_logo_path):
        try:
            logo_img = Image.open(custom_logo_path).convert("RGBA")
            logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Buat mask untuk membuat logo bulat
            mask = Image.new('L', (logo_size, logo_size), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.ellipse((0, 0, logo_size, logo_size), fill=255)

            # Tempatkan logo di posisi yang ditentukan
            img.paste(logo_img, (logo_x, logo_y), mask)
        except Exception as e:
            # Jika terjadi kesalahan saat memuat logo, gunakan placeholder
            draw.ellipse([(logo_x, logo_y), (logo_x + logo_size, logo_y + logo_size)], fill='#e0e0e0')
            draw.text((logo_x + logo_size//2, logo_y + logo_size//2), "LOGO", fill=(0, 0, 0), font=label_font, anchor="mm")
    else:
        # Logo placeholder
        draw.ellipse([(logo_x, logo_y), (logo_x + logo_size, logo_y + logo_size)], fill='#e0e0e0')
        draw.text((logo_x + logo_size//2, logo_y + logo_size//2), "LOGO", fill=(0, 0, 0), font=label_font, anchor="mm")

    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return img_buffer


@cached_document_creation
def create_admission_letter_document(data=None, width=800, height=1000):
    """
    Membuat dokumen surat penerimaan dalam bentuk gambar
    """
    if data is None:
        data = generate_admission_letter_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        header_font = ImageFont.truetype("arial.ttf", 16)
        regular_font = ImageFont.truetype("arial.ttf", 14)
        bold_font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    # Header
    y_offset = 40
    draw.text((40, y_offset), data["university_name"], fill=(0, 0, 0), font=title_font)
    y_offset += 30
    draw.text((40, y_offset), data["university_address"], fill=(0, 0, 0), font=regular_font)
    y_offset += 50
    
    # Date
    draw.text((width - 200, y_offset), f"Date: {data['letter_date']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 30
    
    # Recipient
    draw.text((40, y_offset), f"To: {data['student_name']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((40, y_offset), data["address"], fill=(0, 0, 0), font=regular_font)
    y_offset += 50
    
    # Subject
    draw.text((40, y_offset), "Subject: Admission Offer Letter", fill=(0, 0, 0), font=bold_font)
    y_offset += 40
    
    # Letter content
    lines = data["letter_content"].split('\n')
    for line in lines:
        if line.strip():  # Skip empty lines
            draw.text((40, y_offset), line.strip(), fill=(0, 0, 0), font=regular_font)
            y_offset += 25
    
    # Space for signature
    y_offset += 50
    draw.text((width - 300, y_offset), data["officials"]["dean"], fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((width - 300, y_offset), "Dean of Admissions", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((width - 300, y_offset), data["university_name"], fill=(0, 0, 0), font=regular_font)
    
    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


@cached_document_creation
def create_enrollment_certificate_document(data=None, width=800, height=1000):
    """
    Membuat dokumen sertifikat pendaftaran dalam bentuk gambar
    """
    if data is None:
        data = generate_enrollment_certificate_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font
    try:
        title_font = ImageFont.truetype("times.ttf", 24)
        header_font = ImageFont.truetype("times.ttf", 18)
        regular_font = ImageFont.truetype("times.ttf", 16)
        bold_font = ImageFont.truetype("times.ttf", 16)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    # Header
    y_offset = 100
    draw.text((width//2, y_offset), "CERTIFICATE OF ENROLLMENT", fill=(0, 0, 0), font=title_font, anchor="mm")
    y_offset += 50
    draw.line([(100, y_offset), (width-100, y_offset)], fill=(0, 0, 0), width=2)
    
    # Certificate content
    y_offset += 30
    lines = data["certificate_content"].split('\n')
    for line in lines:
        if line.strip():  # Skip empty lines
            draw.text((width//2, y_offset), line.strip(), fill=(0, 0, 0), font=regular_font, anchor="mm")
            y_offset += 25
    
    # Date and registration number
    y_offset += 30
    draw.text((width//2, y_offset), f"Issued on: {data['certificate_date']}", fill=(0, 0, 0), font=regular_font, anchor="mm")
    y_offset += 25
    draw.text((width//2, y_offset), f"Registration Number: {data['registration_number']}", fill=(0, 0, 0), font=regular_font, anchor="mm")
    
    # Signature area
    y_offset += 60
    draw.text((200, y_offset), "_______________________", fill=(0, 0, 0), font=regular_font)
    draw.text((500, y_offset), "_______________________", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((200, y_offset), "Registrar", fill=(0, 0, 0), font=regular_font)
    draw.text((500, y_offset), "Dean of Students", fill=(0, 0, 0), font=regular_font)
    
    # University seal area
    y_offset += 60
    draw.ellipse([(width//2 - 50, y_offset), (width//2 + 50, y_offset + 100)], outline=(0, 0, 0), width=2)
    draw.text((width//2, y_offset + 50), "SEAL", fill=(0, 0, 0), font=bold_font, anchor="mm")
    
    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


@cached_document_creation
def create_schedule_document(data=None, width=800, height=1000):
    """
    Membuat dokumen jadwal kuliah dalam bentuk gambar
    """
    if data is None:
        data = generate_schedule_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        header_font = ImageFont.truetype("arial.ttf", 18)
        regular_font = ImageFont.truetype("arial.ttf", 14)
        bold_font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    # Header
    y_offset = 40
    draw.text((width//2, y_offset), f"{data['university_name']} - Class Schedule", fill=(0, 0, 0), font=title_font, anchor="mm")
    y_offset += 40
    draw.text((width//2, y_offset), f"Student: {data['student_name']}", fill=(0, 0, 0), font=header_font, anchor="mm")
    y_offset += 25
    draw.text((width//2, y_offset), f"Student ID: {data['student_id']}", fill=(0, 0, 0), font=regular_font, anchor="mm")
    y_offset += 25
    draw.text((width//2, y_offset), f"Semester: {data['semester']}", fill=(0, 0, 0), font=regular_font, anchor="mm")
    y_offset += 50
    
    # Schedule table headers
    day_col = 50
    time_col = 200
    course_col = 350
    location_col = 600
    
    draw.rectangle([(day_col, y_offset), (width-50, y_offset+30)], fill=(240, 240, 240))
    draw.text((day_col+10, y_offset+8), "Day", fill=(0, 0, 0), font=bold_font)
    draw.text((time_col, y_offset+8), "Time", fill=(0, 0, 0), font=bold_font)
    draw.text((course_col, y_offset+8), "Course", fill=(0, 0, 0), font=bold_font)
    draw.text((location_col, y_offset+8), "Location", fill=(0, 0, 0), font=bold_font)
    
    y_offset += 30
    
    # Schedule rows
    current_day = ""
    for item in data["schedule"]:
        # Draw day header if new day
        if item["day"] != current_day:
            current_day = item["day"]
            draw.rectangle([(day_col, y_offset), (width-50, y_offset+25)], fill=(250, 250, 250))
            day_text = f"--- {current_day} ---"
            draw.text((width//2, y_offset+5), day_text, fill=(0, 0, 0), font=bold_font, anchor="mm")
            y_offset += 25
        
        # Draw schedule item
        draw.line([(day_col, y_offset), (width-50, y_offset)], fill=(200, 200, 200), width=1)
        draw.text((day_col+10, y_offset+5), item["day"], fill=(0, 0, 0), font=regular_font)
        draw.text((time_col, y_offset+5), item["time"], fill=(0, 0, 0), font=regular_font)
        draw.text((course_col, y_offset+5), f"{item['course_code']} - {item['course_name']}", fill=(0, 0, 0), font=regular_font)
        draw.text((location_col, y_offset+5), item["location"], fill=(0, 0, 0), font=regular_font)
        y_offset += 25
    
    # Footer
    y_offset += 30
    draw.text((50, y_offset), "Note: This schedule is subject to change. Please check with the registrar for updates.", fill=(100, 100, 100), font=regular_font)
    
    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


@cached_document_creation
def create_employment_letter_document(data=None, width=800, height=1000):
    """
    Membuat dokumen surat kerja guru dalam bentuk gambar
    """
    if data is None:
        data = generate_employment_letter_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        header_font = ImageFont.truetype("arial.ttf", 16)
        regular_font = ImageFont.truetype("arial.ttf", 14)
        bold_font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    # Header
    y_offset = 40
    draw.text((40, y_offset), data["university_name"], fill=(0, 0, 0), font=title_font)
    draw.text((width - 200, y_offset), f"Date: {data['letter_date']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((40, y_offset), f"{data['university_address']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 40
    
    # To
    draw.text((40, y_offset), f"To: {data['teacher_full_name']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((40, y_offset), data["address"], fill=(0, 0, 0), font=regular_font)
    y_offset += 40
    
    # Subject
    draw.text((40, y_offset), "Subject: Employment Confirmation Letter", fill=(0, 0, 0), font=bold_font)
    y_offset += 40
    
    # Letter content
    lines = data["letter_content"].split('\n')
    for line in lines:
        if line.strip():  # Skip empty lines
            draw.text((40, y_offset), line.strip(), fill=(0, 0, 0), font=regular_font)
            y_offset += 25
    
    # Space for signature
    y_offset += 50
    draw.text((width - 300, y_offset), data["officials"]["dean"], fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((width - 300, y_offset), "Dean of Faculty Affairs", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((width - 300, y_offset), data["university_name"], fill=(0, 0, 0), font=regular_font)
    
    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


@cached_document_creation
def create_salary_statement_document(data=None, width=800, height=1000):
    """
    Membuat dokumen pernyataan gaji guru dalam bentuk gambar
    """
    if data is None:
        data = generate_salary_statement_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font
    try:
        title_font = ImageFont.truetype("arial.ttf", 20)
        header_font = ImageFont.truetype("arial.ttf", 16)
        regular_font = ImageFont.truetype("arial.ttf", 14)
        bold_font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    # Header
    y_offset = 40
    draw.text((40, y_offset), data["university_name"], fill=(0, 0, 0), font=title_font)
    y_offset += 20
    draw.text((40, y_offset), data["university_address"], fill=(0, 0, 0), font=regular_font)
    y_offset += 40
    
    # Title
    draw.text((width//2, y_offset), "SALARY STATEMENT", fill=(0, 0, 0), font=title_font, anchor="mm")
    y_offset += 30
    
    # Employee info
    draw.text((40, y_offset), f"Employee Name: {data['teacher_full_name']}", fill=(0, 0, 0), font=regular_font)
    draw.text((width - 200, y_offset), f"Employee ID: {data['employee_id']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((40, y_offset), f"Position: {data['position']}", fill=(0, 0, 0), font=regular_font)
    draw.text((width - 200, y_offset), f"Department: {data['department']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 30
    
    # Pay period
    draw.text((40, y_offset), f"Pay Period: {data['pay_period_start']} to {data['pay_period_end']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 40
    
    # Earnings section
    draw.text((40, y_offset), "EARNINGS", fill=(0, 0, 0), font=bold_font)
    y_offset += 25
    draw.text((40, y_offset), f"Base Salary: {data['salary_formatted']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((40, y_offset), f"Gross Pay: {data['gross_pay']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 40
    
    # Deductions section
    draw.text((40, y_offset), "DEDUCTIONS", fill=(0, 0, 0), font=bold_font)
    y_offset += 25
    for deduction, amount in data["deductions"].items():
        deduction_name = deduction.replace('_', ' ').title()
        draw.text((40, y_offset), f"{deduction_name}: ${amount:.2f}", fill=(0, 0, 0), font=regular_font)
        y_offset += 20
    y_offset += 10
    
    # Net pay
    draw.text((40, y_offset), f"Net Pay: {data['net_pay']}", fill=(0, 0, 0), font=bold_font)
    y_offset += 40
    
    # Payment method
    draw.text((40, y_offset), f"Payment Method: {data['payment_method']}", fill=(0, 0, 0), font=regular_font)
    draw.text((width - 250, y_offset), f"Account: {data['account_info']}", fill=(0, 0, 0), font=regular_font)
    y_offset += 60
    
    # Authorized signature
    draw.text((width - 200, y_offset), "_________________________", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((width - 200, y_offset), "HR Director", fill=(0, 0, 0), font=regular_font)
    
    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


@cached_document_creation
def create_teaching_certificate_document(data=None, width=800, height=1000):
    """
    Membuat dokumen sertifikat mengajar guru dalam bentuk gambar
    """
    if data is None:
        data = generate_teaching_certificate_data()

    # Membuat gambar dengan ukuran yang dapat disesuaikan
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Font
    try:
        title_font = ImageFont.truetype("times.ttf", 24)
        header_font = ImageFont.truetype("times.ttf", 18)
        regular_font = ImageFont.truetype("times.ttf", 16)
        bold_font = ImageFont.truetype("times.ttf", 16)
    except IOError:
        # Jika font tidak ditemukan, gunakan default
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    # Header
    y_offset = 100
    draw.text((width//2, y_offset), "TEACHING CERTIFICATE", fill=(0, 0, 0), font=title_font, anchor="mm")
    y_offset += 50
    draw.line([(100, y_offset), (width-100, y_offset)], fill=(0, 0, 0), width=2)
    
    # Certificate content
    y_offset += 30
    lines = data["certificate_content"].split('\n')
    for line in lines:
        if line.strip():  # Skip empty lines
            draw.text((width//2, y_offset), line.strip(), fill=(0, 0, 0), font=regular_font, anchor="mm")
            y_offset += 25
    
    # Date and certificate number
    y_offset += 30
    draw.text((width//2, y_offset), f"Certificate Date: {data['certificate_date']}", fill=(0, 0, 0), font=regular_font, anchor="mm")
    y_offset += 25
    draw.text((width//2, y_offset), f"Certificate Number: {data['certificate_number']}", fill=(0, 0, 0), font=regular_font, anchor="mm")
    
    # Validity period
    y_offset += 25
    draw.text((width//2, y_offset), f"Valid From: {data['valid_from']} To: {data['valid_until']}", fill=(0, 0, 0), font=regular_font, anchor="mm")
    
    # Signature area
    y_offset += 60
    draw.text((200, y_offset), "_______________________", fill=(0, 0, 0), font=regular_font)
    draw.text((500, y_offset), "_______________________", fill=(0, 0, 0), font=regular_font)
    y_offset += 20
    draw.text((200, y_offset), "Dean of Education", fill=(0, 0, 0), font=regular_font)
    draw.text((500, y_offset), "University Chancellor", fill=(0, 0, 0), font=regular_font)
    
    # University seal area
    y_offset += 60
    draw.ellipse([(width//2 - 50, y_offset), (width//2 + 50, y_offset + 100)], outline=(0, 0, 0), width=2)
    draw.text((width//2, y_offset + 50), "OFFICIAL SEAL", fill=(0, 0, 0), font=bold_font, anchor="mm")
    
    # Simpan ke BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer



def validate_document_quality(image_buffer, min_width=800, min_height=600, max_file_size=5*1024*1024):
    """
    Memvalidasi kualitas dokumen yang dihasilkan
    """
    try:
        # Cek ukuran file
        image_buffer.seek(0, 2)  # Pindah ke akhir file
        file_size = image_buffer.tell()
        image_buffer.seek(0)  # Kembali ke awal

        if file_size > max_file_size:
            return {"valid": False, "error": f"File size too large: {file_size} bytes (> {max_file_size})"}

        # Cek dimensi gambar
        from PIL import Image
        image = Image.open(image_buffer)
        width, height = image.size

        if width < min_width or height < min_height:
            return {"valid": False, "error": f"Image dimensions too small: {width}x{height} (< {min_width}x{min_height})"}

        # Cek format gambar
        if image.format not in ['PNG', 'JPEG', 'JPG']:
            return {"valid": False, "error": f"Unsupported image format: {image.format}"}

        return {"valid": True, "size": (width, height), "file_size": file_size}

    except Exception as e:
        return {"valid": False, "error": f"Error validating document: {str(e)}"}


def create_multiple_documents(student_data=None, teacher_data=None,
                           transcript_size=(800, 1000), tuition_size=(800, 1000),
                           student_id_size=(750, 480), letter_size=(800, 1000),
                           certificate_size=(800, 1000), schedule_size=(800, 1000),
                           custom_logo_path=None):
    """
    Membuat beberapa dokumen sekaligus untuk verifikasi pelajar atau guru
    """
    if student_data is None:
        student_data = generate_random_data()

    if teacher_data is None:
        teacher_data = generate_teacher_data()

    documents = {}

    # Jika data pelajar tersedia, buat dokumen pelajar
    if "student_name" in student_data:
        documents["transcript"] = create_transcript_document(student_data, width=transcript_size[0], height=transcript_size[1])
        documents["tuition"] = create_tuition_document(student_data, width=tuition_size[0], height=tuition_size[1])
        documents["admission_letter"] = create_admission_letter_document(student_data, width=letter_size[0], height=letter_size[1])
        documents["enrollment_certificate"] = create_enrollment_certificate_document(student_data, width=certificate_size[0], height=certificate_size[1])
        documents["schedule"] = create_schedule_document(student_data, width=schedule_size[0], height=schedule_size[1])
        documents["student_id_front"] = create_student_id_front(student_data, width=student_id_size[0], height=student_id_size[1], custom_logo_path=custom_logo_path)
        documents["student_id_back"] = create_student_id_back(student_data, width=student_id_size[0], height=student_id_size[1], custom_logo_path=custom_logo_path)

    # Jika data guru tersedia, buat dokumen guru
    if "teacher_name" in teacher_data:
        documents["employment_letter"] = create_employment_letter_document(teacher_data, width=letter_size[0], height=letter_size[1])
        documents["salary_statement"] = create_salary_statement_document(teacher_data, width=letter_size[0], height=letter_size[1])
        documents["teaching_certificate"] = create_teaching_certificate_document(teacher_data, width=certificate_size[0], height=certificate_size[1])
        # Note: Teacher ID creation would need separate function if needed

    return documents