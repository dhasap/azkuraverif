"""K12 Teacher Badge Generator
Replaces old HTML-based generator with Pillow for better performance and look
"""
import os
import random
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_teacher_badge(first_name: str, last_name: str, school_name: str) -> bytes:
    """Generate fake K12 teacher badge PNG"""
    width, height = 500, 350
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Load fonts (fallback to default if arial not found)
    try:
        # Try finding fonts in standard linux paths
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(font_path):
            font_path = "arial.ttf" # Fallback
            
        title_font = ImageFont.truetype(font_path, 22)
        text_font = ImageFont.truetype(font_path, 16)
        small_font = ImageFont.truetype(font_path, 12)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Header bar (Forest Green for K12 vibe)
    draw.rectangle([(0, 0), (width, 50)], fill=(34, 139, 34)) 
    
    # Title centered
    title_text = "STAFF IDENTIFICATION"
    # Basic centering logic since anchor='mm' might vary by Pillow version
    text_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text(((width - text_width) / 2, 15), title_text, fill=(255, 255, 255), font=title_font)
    
    # School name centered
    school_name = school_name[:40] # Truncate if too long
    text_bbox = draw.textbbox((0, 0), school_name, font=text_font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text(((width - text_width) / 2, 75), school_name, fill=(34, 139, 34), font=text_font)
    
    # Photo placeholder
    draw.rectangle([(25, 100), (125, 220)], outline=(200, 200, 200), width=2)
    draw.text((55, 150), "PHOTO", fill=(200, 200, 200), font=text_font)
    
    # Teacher info
    teacher_id = f"T{random.randint(10000, 99999)}"
    info_y = 110
    info_lines = [
        f"Name: {first_name} {last_name}",
        f"ID: {teacher_id}",
        f"Position: Teacher",
        f"Department: Education",
        f"Status: Active"
    ]
    
    for line in info_lines:
        draw.text((145, info_y), line, fill=(51, 51, 51), font=text_font)
        info_y += 22
    
    # Valid date
    current_year = int(time.strftime("%Y"))
    valid_text = f"Valid: {current_year}-{current_year+1} School Year"
    draw.text((145, info_y + 10), valid_text, fill=(100, 100, 100), font=small_font)
    
    # Footer
    draw.rectangle([(0, height-35), (width, height)], fill=(34, 139, 34))
    
    footer_text = "Property of School District"
    text_bbox = draw.textbbox((0, 0), footer_text, font=small_font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text(((width - text_width) / 2, height-25), footer_text, fill=(255, 255, 255), font=small_font)
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# Compatibility wrapper
def generate_teacher_image(first_name: str, last_name: str) -> bytes:
    # Use a generic name if school not provided, though it should be
    return generate_teacher_badge(first_name, last_name, "Thomas Jefferson High School")

async def generate_teacher_png(first_name: str, last_name: str) -> bytes:
    """Async wrapper for compatibility"""
    return generate_teacher_image(first_name, last_name)

def generate_teacher_pdf(first_name: str, last_name: str) -> bytes:
    """Generate a PDF containing the teacher badge"""
    png_bytes = generate_teacher_image(first_name, last_name)
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Draw image from bytes using a temporary file or ImageReader
    # ReportLab ImageReader can take BytesIO
    from reportlab.lib.utils import ImageReader
    image = ImageReader(BytesIO(png_bytes))
    
    # Center the image roughly
    img_width = 400
    img_height = 280 # Proportional to 500x350
    x = (width - img_width) / 2
    y = (height - img_height) / 2
    
    c.drawImage(image, x, y, width=img_width, height=img_height)
    
    c.setFont("Helvetica", 12)
    c.drawString(x, y - 20, "Official Teacher Identification Document")
    
    c.save()
    return buffer.getvalue()