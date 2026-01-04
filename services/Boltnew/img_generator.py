"""Bolt.new Employment Certificate Generator
Generates a professional employment verification letter instead of ID card.
"""
import os
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def generate_employment_certificate(first_name: str, last_name: str, school_name: str) -> bytes:
    """Generate fake teacher employment certificate PNG"""
    width, height = 800, 500
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" # Common on linux
        if not os.path.exists(font_path):
            font_path = "arial.ttf"
            
        title_font = ImageFont.truetype(font_path, 32)
        text_font = ImageFont.truetype(font_path, 24)
        small_font = ImageFont.truetype(font_path, 18)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Border
    draw.rectangle([(20, 20), (width-20, height-20)], outline=(0, 51, 102), width=3)
    
    # Title
    title = "FACULTY EMPLOYMENT VERIFICATION"
    
    # Manual centering
    text_bbox = draw.textbbox((0, 0), title, font=title_font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text(((width - text_width) / 2, 50), title, fill=(0, 51, 102), font=title_font)
    
    # Divider
    draw.line([(50, 100), (width-50, 100)], fill=(0, 51, 102), width=2)
    
    # School Name
    text_bbox = draw.textbbox((0, 0), school_name, font=text_font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text(((width - text_width) / 2, 120), school_name, fill=(51, 51, 51), font=text_font)
    
    # Info
    y = 180
    info_lines = [
        f"Employee Name: {first_name} {last_name}",
        f"Position: Faculty Member",
        f"Department: Education",
        f"Employment Status: Active",
        f"Issue Date: {time.strftime('%B %d, %Y')}"
    ]
    
    for line in info_lines:
        draw.text((100, y), line, fill=(51, 51, 51), font=text_font)
        y += 45
    
    # Footer
    footer = "This document verifies current employment status."
    text_bbox = draw.textbbox((0, 0), footer, font=small_font)
    text_width = text_bbox[2] - text_bbox[0]
    draw.text(((width - text_width) / 2, height-60), footer, fill=(128, 128, 128), font=small_font)
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

# Wrapper for compatibility
def generate_teacher_card_html(first_name, last_name, psu_id):
    # This function name is legacy, we just return bytes now but the caller expects HTML string?
    # No, the new verifier will call this generator directly.
    pass

def generate_images(first_name, last_name, school_name="Pennsylvania State University"):
    """
    Returns list of assets for the new verifier logic
    """
    data = generate_employment_certificate(first_name, last_name, school_name)
    return [
        {"file_name": "employment_cert.png", "data": data}
    ]