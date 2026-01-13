"""
Modul untuk membuat ID card pelajar dan lainnya
"""

from PIL import Image, ImageDraw, ImageFont
import os
import uuid
from datetime import datetime, timedelta


class IDCardGenerator:
    """
    Kelas untuk membuat berbagai jenis ID card
    """
    
    def __init__(self):
        # Direktori untuk menyimpan ID card yang dihasilkan
        self.output_dir = "output/id_cards"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Path font - coba beberapa kemungkinan lokasi font
        self.font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Arial.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "./assets/fonts/DejaVuSans.ttf"
        ]
        
        # Cari font yang tersedia
        self.font_path = None
        for path in self.font_paths:
            if os.path.exists(path):
                self.font_path = path
                break
        
        # Gunakan font default jika tidak ada font yang ditemukan
        if self.font_path is None:
            self.font_regular = ImageFont.load_default()
            self.font_bold = ImageFont.load_default()
        else:
            self.font_regular = ImageFont.truetype(self.font_path, 16)
            self.font_bold = ImageFont.truetype(self.font_path, 20)
    
    def create_student_id(self, name, institution, student_id, photo_path=None, expiry_date=None):
        """
        Membuat ID card pelajar
        """
        # Ukuran ID card standar (dalam piksel, sekitar 3.375 x 2.125 inci pada 300 DPI)
        width, height = 1013, 638
        id_card = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(id_card)
        
        # Warna tema
        header_color = (0, 51, 102)  # Biru gelap
        accent_color = (0, 102, 204)  # Biru muda
        text_color = (0, 0, 0)  # Hitam
        
        # Header
        header_height = 120
        draw.rectangle([0, 0, width, header_height], fill=header_color)
        
        # Teks header
        header_text = "STUDENT ID"
        bbox = draw.textbbox((0, 0), header_text, font=self.font_bold)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, 30), header_text, fill="white", font=self.font_bold)
        
        # Logo institusi (placeholder)
        logo_size = 80
        logo_x = 30
        logo_y = (header_height - logo_size) // 2
        draw.rectangle([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                      fill=accent_color, outline="white", width=2)
        
        # Tambahkan teks "LOGO" di tengah kotak
        logo_text = "LOGO"
        bbox = draw.textbbox((0, 0), logo_text, font=self.font_regular)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text((logo_x + (logo_size - text_width) // 2, 
                  logo_y + (logo_size - text_height) // 2), 
                 logo_text, fill="white", font=self.font_regular)
        
        # Informasi pelajar
        info_start_y = header_height + 30
        line_spacing = 40
        
        # Nama
        draw.text((50, info_start_y), f"Name:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y), name, fill=text_color, font=self.font_bold)
        
        # Institusi
        draw.text((50, info_start_y + line_spacing), f"Institution:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing), institution, fill=text_color, font=self.font_regular)
        
        # ID Pelajar
        draw.text((50, info_start_y + line_spacing * 2), f"Student ID:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing * 2), student_id, fill=text_color, font=self.font_regular)
        
        # Tanggal kadaluarsa
        if expiry_date is None:
            expiry_date = datetime.now() + timedelta(days=365)  # 1 tahun dari sekarang
        expiry_str = expiry_date.strftime("%m/%d/%Y")
        draw.text((50, info_start_y + line_spacing * 3), f"Expiry Date:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing * 3), expiry_str, fill=text_color, font=self.font_regular)
        
        # Foto pelajar
        if photo_path and os.path.exists(photo_path):
            try:
                photo = Image.open(photo_path)
                photo = photo.convert('RGB')
                
                # Resize foto ke ukuran yang sesuai
                photo_size = (180, 220)
                photo = photo.resize(photo_size, Image.Resampling.LANCZOS)
                
                # Simpan foto ke posisi yang ditentukan
                photo_x = width - 230
                photo_y = info_start_y
                id_card.paste(photo, (photo_x, photo_y))
            except Exception as e:
                print(f"Error loading photo: {e}")
        else:
            # Placeholder untuk foto
            photo_x = width - 230
            photo_y = info_start_y
            photo_size = (180, 220)
            draw.rectangle([photo_x, photo_y, photo_x + photo_size[0], photo_y + photo_size[1]], 
                          fill=(240, 240, 240), outline="black", width=1)
            
            # Tambahkan teks "PHOTO" di tengah placeholder
            photo_text = "PHOTO"
            bbox = draw.textbbox((0, 0), photo_text, font=self.font_regular)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((photo_x + (photo_size[0] - text_width) // 2, 
                      photo_y + (photo_size[1] - text_height) // 2), 
                     photo_text, fill=text_color, font=self.font_regular)
        
        # Footer
        footer_y = height - 40
        draw.line([(50, footer_y), (width - 50, footer_y)], fill=text_color, width=1)
        
        # Barcode placeholder
        barcode_y = footer_y + 10
        draw.rectangle([50, barcode_y, width - 50, barcode_y + 20], fill=text_color)
        
        # Simpan ID card
        filename = f"student_id_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        id_card.save(filepath, "JPEG", quality=95)
        
        return filepath
    
    def create_teacher_id(self, name, institution, employee_id, photo_path=None, expiry_date=None):
        """
        Membuat ID card guru
        """
        # Ukuran ID card standar (dalam piksel, sekitar 3.375 x 2.125 inci pada 300 DPI)
        width, height = 1013, 638
        id_card = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(id_card)
        
        # Warna tema
        header_color = (139, 69, 19)  # Coklat
        accent_color = (205, 133, 63)  # Coklat muda
        text_color = (0, 0, 0)  # Hitam
        
        # Header
        header_height = 120
        draw.rectangle([0, 0, width, header_height], fill=header_color)
        
        # Teks header
        header_text = "TEACHER ID"
        bbox = draw.textbbox((0, 0), header_text, font=self.font_bold)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, 30), header_text, fill="white", font=self.font_bold)
        
        # Logo institusi (placeholder)
        logo_size = 80
        logo_x = 30
        logo_y = (header_height - logo_size) // 2
        draw.rectangle([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                      fill=accent_color, outline="white", width=2)
        
        # Tambahkan teks "LOGO" di tengah kotak
        logo_text = "LOGO"
        bbox = draw.textbbox((0, 0), logo_text, font=self.font_regular)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text((logo_x + (logo_size - text_width) // 2, 
                  logo_y + (logo_size - text_height) // 2), 
                 logo_text, fill="white", font=self.font_regular)
        
        # Informasi guru
        info_start_y = header_height + 30
        line_spacing = 40
        
        # Nama
        draw.text((50, info_start_y), f"Name:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y), name, fill=text_color, font=self.font_bold)
        
        # Institusi
        draw.text((50, info_start_y + line_spacing), f"Institution:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing), institution, fill=text_color, font=self.font_regular)
        
        # ID Guru
        draw.text((50, info_start_y + line_spacing * 2), f"Employee ID:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing * 2), employee_id, fill=text_color, font=self.font_regular)
        
        # Tanggal kadaluarsa
        if expiry_date is None:
            expiry_date = datetime.now() + timedelta(days=365)  # 1 tahun dari sekarang
        expiry_str = expiry_date.strftime("%m/%d/%Y")
        draw.text((50, info_start_y + line_spacing * 3), f"Expiry Date:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing * 3), expiry_str, fill=text_color, font=self.font_regular)
        
        # Foto guru
        if photo_path and os.path.exists(photo_path):
            try:
                photo = Image.open(photo_path)
                photo = photo.convert('RGB')
                
                # Resize foto ke ukuran yang sesuai
                photo_size = (180, 220)
                photo = photo.resize(photo_size, Image.Resampling.LANCZOS)
                
                # Simpan foto ke posisi yang ditentukan
                photo_x = width - 230
                photo_y = info_start_y
                id_card.paste(photo, (photo_x, photo_y))
            except Exception as e:
                print(f"Error loading photo: {e}")
        else:
            # Placeholder untuk foto
            photo_x = width - 230
            photo_y = info_start_y
            photo_size = (180, 220)
            draw.rectangle([photo_x, photo_y, photo_x + photo_size[0], photo_y + photo_size[1]], 
                          fill=(240, 240, 240), outline="black", width=1)
            
            # Tambahkan teks "PHOTO" di tengah placeholder
            photo_text = "PHOTO"
            bbox = draw.textbbox((0, 0), photo_text, font=self.font_regular)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((photo_x + (photo_size[0] - text_width) // 2, 
                      photo_y + (photo_size[1] - text_height) // 2), 
                     photo_text, fill=text_color, font=self.font_regular)
        
        # Footer
        footer_y = height - 40
        draw.line([(50, footer_y), (width - 50, footer_y)], fill=text_color, width=1)
        
        # Barcode placeholder
        barcode_y = footer_y + 10
        draw.rectangle([50, barcode_y, width - 50, barcode_y + 20], fill=text_color)
        
        # Simpan ID card
        filename = f"teacher_id_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        id_card.save(filepath, "JPEG", quality=95)
        
        return filepath
    
    def create_military_id(self, name, branch, rank, military_id, photo_path=None, expiry_date=None):
        """
        Membuat ID card militer
        """
        # Ukuran ID card standar (dalam piksel, sekitar 3.375 x 2.125 inci pada 300 DPI)
        width, height = 1013, 638
        id_card = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(id_card)
        
        # Warna tema
        header_color = (0, 100, 0)  # Hijau darat
        accent_color = (34, 139, 34)  # Hijau hutan
        text_color = (0, 0, 0)  # Hitam
        
        # Header
        header_height = 120
        draw.rectangle([0, 0, width, header_height], fill=header_color)
        
        # Teks header
        header_text = "MILITARY ID"
        bbox = draw.textbbox((0, 0), header_text, font=self.font_bold)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, 30), header_text, fill="white", font=self.font_bold)
        
        # Logo militer (placeholder)
        logo_size = 80
        logo_x = 30
        logo_y = (header_height - logo_size) // 2
        draw.rectangle([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], 
                      fill=accent_color, outline="white", width=2)
        
        # Tambahkan teks "MILITARY" di tengah kotak
        logo_text = "MILITARY"
        bbox = draw.textbbox((0, 0), logo_text, font=self.font_regular)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text((logo_x + (logo_size - text_width) // 2, 
                  logo_y + (logo_size - text_height) // 2), 
                 logo_text, fill="white", font=self.font_regular)
        
        # Informasi militer
        info_start_y = header_height + 30
        line_spacing = 40
        
        # Nama
        draw.text((50, info_start_y), f"Name:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y), name, fill=text_color, font=self.font_bold)
        
        # Pangkat
        draw.text((50, info_start_y + line_spacing), f"Rank:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing), rank, fill=text_color, font=self.font_regular)
        
        # Cabang Militer
        draw.text((50, info_start_y + line_spacing * 2), f"Branch:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing * 2), branch, fill=text_color, font=self.font_regular)
        
        # ID Militer
        draw.text((50, info_start_y + line_spacing * 3), f"Military ID:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing * 3), military_id, fill=text_color, font=self.font_regular)
        
        # Tanggal kadaluarsa
        if expiry_date is None:
            expiry_date = datetime.now() + timedelta(days=365)  # 1 tahun dari sekarang
        expiry_str = expiry_date.strftime("%m/%d/%Y")
        draw.text((50, info_start_y + line_spacing * 4), f"Expiry Date:", fill=text_color, font=self.font_regular)
        draw.text((200, info_start_y + line_spacing * 4), expiry_str, fill=text_color, font=self.font_regular)
        
        # Foto militer
        if photo_path and os.path.exists(photo_path):
            try:
                photo = Image.open(photo_path)
                photo = photo.convert('RGB')
                
                # Resize foto ke ukuran yang sesuai
                photo_size = (180, 220)
                photo = photo.resize(photo_size, Image.Resampling.LANCZOS)
                
                # Simpan foto ke posisi yang ditentukan
                photo_x = width - 230
                photo_y = info_start_y
                id_card.paste(photo, (photo_x, photo_y))
            except Exception as e:
                print(f"Error loading photo: {e}")
        else:
            # Placeholder untuk foto
            photo_x = width - 230
            photo_y = info_start_y
            photo_size = (180, 220)
            draw.rectangle([photo_x, photo_y, photo_x + photo_size[0], photo_y + photo_size[1]], 
                          fill=(240, 240, 240), outline="black", width=1)
            
            # Tambahkan teks "PHOTO" di tengah placeholder
            photo_text = "PHOTO"
            bbox = draw.textbbox((0, 0), photo_text, font=self.font_regular)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((photo_x + (photo_size[0] - text_width) // 2, 
                      photo_y + (photo_size[1] - text_height) // 2), 
                     photo_text, fill=text_color, font=self.font_regular)
        
        # Footer
        footer_y = height - 40
        draw.line([(50, footer_y), (width - 50, footer_y)], fill=text_color, width=1)
        
        # Barcode placeholder
        barcode_y = footer_y + 10
        draw.rectangle([50, barcode_y, width - 50, barcode_y + 20], fill=text_color)
        
        # Simpan ID card
        filename = f"military_id_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        id_card.save(filepath, "JPEG", quality=95)
        
        return filepath


# Fungsi helper untuk membuat ID card
def generate_id_card(card_type, name, institution_or_branch, id_number, photo_path=None, expiry_date=None):
    """
    Fungsi helper untuk membuat ID card berdasarkan tipe
    """
    generator = IDCardGenerator()
    
    if card_type == "student":
        return generator.create_student_id(
            name=name,
            institution=institution_or_branch,
            student_id=id_number,
            photo_path=photo_path,
            expiry_date=expiry_date
        )
    elif card_type == "teacher":
        return generator.create_teacher_id(
            name=name,
            institution=institution_or_branch,
            employee_id=id_number,
            photo_path=photo_path,
            expiry_date=expiry_date
        )
    elif card_type == "military":
        # Untuk ID militer, kita perlu memecah informasi tambahan
        # Misalnya, id_number bisa berupa dictionary dengan rank dan military_id
        if isinstance(id_number, dict):
            rank = id_number.get("rank", "")
            military_id = id_number.get("military_id", "")
            return generator.create_military_id(
                name=name,
                branch=institution_or_branch,
                rank=rank,
                military_id=military_id,
                photo_path=photo_path,
                expiry_date=expiry_date
            )
        else:
            raise ValueError("Untuk ID militer, id_number harus berupa dictionary dengan rank dan military_id")
    else:
        raise ValueError(f"Tipe ID card '{card_type}' tidak didukung")


if __name__ == "__main__":
    # Contoh penggunaan
    generator = IDCardGenerator()
    
    # Buat ID card pelajar contoh
    student_id_path = generator.create_student_id(
        name="John Doe",
        institution="University of Technology",
        student_id="STD-001",
        expiry_date=datetime.now() + timedelta(days=365)
    )
    
    print(f"ID card pelajar dibuat: {student_id_path}")
    
    # Buat ID card guru contoh
    teacher_id_path = generator.create_teacher_id(
        name="Jane Smith",
        institution="University of Technology",
        employee_id="EMP-001",
        expiry_date=datetime.now() + timedelta(days=365)
    )
    
    print(f"ID card guru dibuat: {teacher_id_path}")
    
    # Buat ID card militer contoh
    military_id_path = generator.create_military_id(
        name="Robert Johnson",
        branch="Army",
        rank="Sergeant",
        military_id="MIL-001",
        expiry_date=datetime.now() + timedelta(days=365)
    )
    
    print(f"ID card militer dibuat: {military_id_path}")