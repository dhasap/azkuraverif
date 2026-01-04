"""Groningen Invoice Generator
Generates realistic tuition fee invoice for University of Groningen
"""
import random
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os

def generate_groningen_invoice(first_name: str, last_name: str, dob: str) -> bytes:
    """Generate Groningen tuition fee invoice"""
    # A4 size at 72 DPI (approx)
    w, h = 595, 842 
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
        if not os.path.exists(font_path):
            font_path = "arial.ttf"
            font_bold_path = "arialbd.ttf"
            
        font_uni = ImageFont.truetype(font_path, 16)
        font_header = ImageFont.truetype(font_path, 10)
        font_title = ImageFont.truetype(font_path, 12)
        font_text = ImageFont.truetype(font_path, 10)
        font_small = ImageFont.truetype(font_path, 8)
        font_bold = ImageFont.truetype(font_bold_path, 10)
    except:
        font_uni = font_header = font_title = font_text = font_small = font_bold = ImageFont.load_default()
    
    # Colors
    rug_red = (204, 0, 0)
    black = (0, 0, 0)
    gray = (100, 100, 100)
    
    # ===== HEADER =====
    # Logo text fallback
    draw.rectangle([(40, 30), (65, 70)], fill=rug_red)
    draw.text((70, 35), "university of", fill=rug_red, font=font_header)
    draw.text((70, 48), "groningen", fill=rug_red, font=font_uni)
    
    # Middle header
    draw.text((200, 35), "university services", fill=gray, font=font_header)
    
    # Right header
    draw.text((380, 30), "student information and", fill=gray, font=font_header)
    draw.text((380, 42), "administration", fill=gray, font=font_header)
    draw.text((380, 56), "050 363 8233", fill=gray, font=font_small)
    draw.text((380, 68), "www.rug.nl/insandouts", fill=gray, font=font_small)
    
    # Address block (right)
    draw.text((420, 90), "Broerstraat 5", fill=gray, font=font_small)
    draw.text((420, 100), "Groningen", fill=gray, font=font_small)
    draw.text((420, 110), "PO Box 72", fill=gray, font=font_small)
    draw.text((420, 120), "9700 AB Groningen", fill=gray, font=font_small)
    draw.text((420, 130), "The Netherlands", fill=gray, font=font_small)
    draw.text((420, 145), "www.rug.nl/SIA", fill=gray, font=font_small)
    
    # Recipient name (left)
    name_full = f"{first_name.upper()} {last_name.upper()}"
    draw.text((40, 100), name_full, fill=black, font=font_title)
    
    # ===== DATE & REFERENCE =====
    current_year = int(time.strftime("%Y"))
    month_name = time.strftime("%B")
    invoice_date = f"{random.randint(1, 28)} {month_name} {current_year}"
    ref_code = f"5Re9fe6r4en6ce{random.randint(10, 99)}"
    
    draw.text((40, 180), "Date", fill=gray, font=font_small)
    draw.text((200, 180), "Concerning", fill=gray, font=font_small)
    draw.text((450, 180), ref_code, fill=gray, font=font_small)
    
    draw.text((40, 192), invoice_date, fill=black, font=font_text)
    draw.text((200, 192), "Tuition Fees", fill=black, font=font_text)
    
    # ===== INVOICE TITLE =====
    draw.text((40, 215), "Invoice tuition fees", fill=black, font=font_title)
    
    # ===== STUDENT INFO =====
    student_num = str(random.randint(5000000, 5999999))
    academic_year = f"{current_year}-{current_year + 1}"
    
    y = 240
    labels = ["Student number:", "Name:", "Date of birth:", "For academic year:", "For the study programme(s):", "Tuition fees:"]
    values = [
        student_num,
        f"{first_name} {last_name}",
        dob,  
        academic_year,
        "Bachelor International Business (English taught) Full-time\nGroningen",
        f"€{random.randint(10, 12)},{random.randint(100, 99)}.00"
    ]
    
    for label, value in zip(labels, values):
        draw.text((40, y), label, fill=black, font=font_text)
        if "\n" in value:
            lines = value.split("\n")
            draw.text((180, y), lines[0], fill=black, font=font_text)
            draw.text((180, y + 12), lines[1], fill=black, font=font_text)
            y += 12
        else:
            draw.text((180, y), value, fill=black, font=font_text)
        y += 18
    
    # ===== TRANSFER DETAILS =====
    y += 15
    draw.text((40, y), "Transfer details", fill=black, font=font_bold)
    y += 18
    
    iban = f"NL{random.randint(10, 99)}MLKP{random.randint(1000000000, 9999999999)}"
    transfer_labels = ["Bank account holder:", "IBAN:", "Bank name:", "BIC/SWIFT code:", "Bank address:", "Payment reference:"]
    transfer_values = [
        f"Rijksuniversiteit Groningen {iban} ABN",
        f"AMRO ABNANL2A Gustav Mahlerlaan 10, 1082 PP",
        "Amsterdam, the Netherlands Tuition fees S5643302, Y.",
        "Amman",
        "",
        ""
    ]
    
    for label, value in zip(transfer_labels, transfer_values):
        draw.text((40, y), label, fill=black, font=font_text)
        draw.text((130, y), value, fill=black, font=font_text)
        y += 14
    
    # ===== WARNING TEXT =====
    y += 20
    draw.text((40, y), "Make sure to transfer the tuition fees before the starting date of the programme.", fill=rug_red, font=font_text)
    
    # ===== SIGNATURE FAKE =====
    y += 50
    draw.text((40, y), "T.K. Idema", fill=black, font=font_text)
    y += 12
    draw.text((40, y), "Head of the Student Information and Administration", fill=black, font=font_text)
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
