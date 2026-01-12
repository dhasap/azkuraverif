
import os
import glob
import random
import logging
from typing import Dict, Optional, Tuple

from services.utils.data_generator import generate_random_data
from services.utils.document_generator import create_student_id_front
from services.utils.university_presets import get_university_preset

logger = logging.getLogger(__name__)

def generate_student_id_card(first: str, last: str, org_data: Dict, gender: str = None) -> bytes:
    """
    Generate fake student ID card using presets or random data with REAL ASSETS.
    Centralized helper function for all services.
    """
    # Generate base random data
    data = generate_random_data()
    
    # Cek apakah ada preset manual untuk universitas ini
    # org_data bisa berupa dict dengan key 'id' atau objek lain, pastikan aman
    org_id = org_data.get("id") if isinstance(org_data, dict) else None
    preset = get_university_preset(org_id)
    
    custom_logo = None
    custom_photo = None
    
    # --- LOGIKA PEMILIHAN FOTO ---
    # Gunakan gender yang diberikan untuk sinkronisasi nama-foto
    # Jika gender tidak ada, pilih acak (namun sebaiknya caller sudah menentukan gender)
    target_gender = gender if gender else random.choice(["male", "female"])
    
    # Path relatif dari root project (diasumsikan script jalan dari root)
    # Jika dijalankan dari subfolder, mungkin perlu penyesuaian path
    photo_dir = os.path.join("assets", "photos", target_gender)
    
    if os.path.exists(photo_dir):
        # Cari semua file gambar di folder gender tersebut
        valid_extensions = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
        photo_files = []
        for ext in valid_extensions:
            photo_files.extend(glob.glob(os.path.join(photo_dir, ext)))
        
        if photo_files:
            custom_photo = random.choice(photo_files)
            logger.info(f"Picked random {target_gender} photo: {custom_photo}")
    else:
        logger.warning(f"Photo dir not found: {photo_dir}")

    if preset:
        # Gunakan data manual yang valid
        logger.info(f"Using manual preset for {preset['name']}")
        
        # Generate ID sesuai format kampus
        student_id = preset['id_format']() if callable(preset['id_format']) else str(random.randint(10000000, 99999999))
        
        preset_data = {
            "student_name": f"{first} {last}",
            "university_name": preset['name'],
            "card_subtitle": preset.get('card_title', 'STUDENT ID'),
            "card_color": preset['colors'][0], # Warna utama
            "student_id": student_id,
            "college": random.choice(preset['colleges']),
            "address": preset['address'],
            "card_notice": f"This card is the property of {preset['name']}.",
        }
        
        # Cek apakah logo file ada di assets
        if "logo_file" in preset:
            logo_path = os.path.join("assets", "logos", preset["logo_file"])
            if os.path.exists(logo_path):
                custom_logo = logo_path
                logger.info(f"Loaded custom logo: {logo_path}")
            else:
                logger.warning(f"Logo file missing: {logo_path}")
        
        data.update(preset_data)
    else:
        # Fallback to generic data
        uni_name = org_data.get("name") if isinstance(org_data, dict) else "University"
        data.update({
            "student_name": f"{first} {last}",
            "university_name": uni_name,
        })

    # Create the front of the student ID card
    img_buffer = create_student_id_front(data, custom_logo_path=custom_logo, custom_photo_path=custom_photo)
    return img_buffer.getvalue()
