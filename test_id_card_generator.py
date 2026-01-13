"""
Skrip uji untuk ID card generator
"""
import os
import sys
sys.path.append(os.getcwd())

from services.id_card_generator.id_card_generator import IDCardGenerator, generate_auto_id_card
from datetime import datetime, timedelta

def test_id_card_generator():
    """Fungsi untuk menguji generator ID card"""
    print("🧪 Memulai pengujian ID Card Generator...")
    
    # Buat instance generator
    generator = IDCardGenerator()
    
    # Uji pembuatan ID card pelajar dengan data manual
    print("\n🎓 Menguji pembuatan Student ID (manual)...")
    try:
        student_id_path = generator.create_student_id(
            name="John Doe",
            institution="University of Technology",
            student_id="STD-001",
            expiry_date=datetime.now() + timedelta(days=365)
        )
        print(f"✅ Student ID berhasil dibuat: {student_id_path}")
    except Exception as e:
        print(f"❌ Error saat membuat Student ID: {e}")
    
    # Uji pembuatan ID card guru dengan data manual
    print("\n👨‍🏫 Menguji pembuatan Teacher ID (manual)...")
    try:
        teacher_id_path = generator.create_teacher_id(
            name="Jane Smith",
            institution="University of Technology",
            employee_id="EMP-001",
            expiry_date=datetime.now() + timedelta(days=365)
        )
        print(f"✅ Teacher ID berhasil dibuat: {teacher_id_path}")
    except Exception as e:
        print(f"❌ Error saat membuat Teacher ID: {e}")
    
    # Uji pembuatan ID card militer dengan data manual
    print("\n🎖️ Menguji pembuatan Military ID (manual)...")
    try:
        military_id_path = generator.create_military_id(
            name="Robert Johnson",
            branch="Army",
            rank="Sergeant",
            military_id="MIL-001",
            expiry_date=datetime.now() + timedelta(days=365)
        )
        print(f"✅ Military ID berhasil dibuat: {military_id_path}")
    except Exception as e:
        print(f"❌ Error saat membuat Military ID: {e}")
    
    # Uji pembuatan ID card otomatis
    print("\n🤖 Menguji pembuatan Student ID (otomatis)...")
    try:
        auto_student_id_path = generate_auto_id_card("student")
        print(f"✅ Auto Student ID berhasil dibuat: {auto_student_id_path}")
    except Exception as e:
        print(f"❌ Error saat membuat Auto Student ID: {e}")
    
    print("\n🎉 Pengujian ID Card Generator selesai!")
    
    # Tampilkan informasi tentang file yang dihasilkan
    output_dir = generator.output_dir
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        print(f"\n📁 File ID card yang dihasilkan di {output_dir}:")
        for file in files:
            file_path = os.path.join(output_dir, file)
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size} bytes)")


if __name__ == "__main__":
    test_id_card_generator()