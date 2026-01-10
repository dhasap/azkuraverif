#!/usr/bin/env python3
"""
Script untuk menguji fungsi-fungsi penting di bot AzkuraVerify
"""

import asyncio
import sys
from pathlib import Path

def test_imports():
    """Uji import modul penting"""
    print("🔍 Menguji import modul penting...")
    
    modules_to_test = [
        ("aiogram", "from aiogram import Bot, Dispatcher"),
        ("database", "from database_turso import db"),
        ("config", "import config"),
        ("handlers", "from handlers import start, user_actions, verification, admin, navigation"),
        ("keyboards", "import keyboards"),
    ]
    
    for name, import_stmt in modules_to_test:
        try:
            exec(import_stmt)
            print(f"  ✅ {name}: Berhasil diimport")
        except Exception as e:
            print(f"  ❌ {name}: Gagal - {str(e)}")
    
    print()

def test_verification_services():
    """Uji semua layanan verifikasi"""
    print("🔍 Menguji layanan verifikasi...")
    
    services = [
        "spotify",
        "youtube", 
        "k12",
        "military",
        "one",
        "perplexity",
        "Boltnew"
    ]
    
    for service in services:
        try:
            module_path = f"services.{service}.sheerid_verifier"
            exec(f"from {module_path} import SheerIDVerifier")
            print(f"  ✅ {service}: Class SheerIDVerifier ditemukan")
        except Exception as e:
            print(f"  ❌ {service}: Gagal - {str(e)}")
    
    print()

def test_handlers():
    """Uji handler utama"""
    print("🔍 Menguji handler utama...")
    
    handlers_to_test = [
        ("start", "handlers.start"),
        ("verification", "handlers.verification"),
        ("user_actions", "handlers.user_actions"),
        ("admin", "handlers.admin"),
        ("navigation", "handlers.navigation"),
    ]
    
    for name, module in handlers_to_test:
        try:
            exec(f"from {module} import router")
            print(f"  ✅ {name}: Router ditemukan")
        except Exception as e:
            print(f"  ❌ {name}: Gagal - {str(e)}")
    
    print()

def test_database_connection():
    """Uji koneksi database"""
    print("🔍 Menguji koneksi database...")
    
    try:
        from database_turso import db
        conn = db.get_connection()
        cursor = conn.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        print("  ✅ Koneksi database: Berhasil")
    except Exception as e:
        print(f"  ❌ Koneksi database: Gagal - {str(e)}")
    
    print()

def test_config():
    """Uji konfigurasi"""
    print("🔍 Menguji konfigurasi...")
    
    try:
        import config
        if config.BOT_TOKEN:
            print("  ✅ Token bot: Ditemukan")
        else:
            print("  ⚠️ Token bot: Tidak ditemukan (ini normal untuk lingkungan pengujian)")
        
        if config.TURSO_DATABASE_URL:
            print("  ✅ URL database: Ditemukan")
        else:
            print("  ✅ URL database: Tidak ditemukan (akan menggunakan database lokal)")
        
        print(f"  ✅ Nama aplikasi: {config.APP_NAME}")
        
    except Exception as e:
        print(f"  ❌ Konfigurasi: Gagal - {str(e)}")
    
    print()

def test_keyboards():
    """Uji fungsi keyboard"""
    print("🔍 Menguji fungsi keyboard...")
    
    try:
        import keyboards
        kb = keyboards.main_menu()
        print("  ✅ main_menu(): Berhasil")
        
        kb = keyboards.get_main_keyboard()
        print("  ✅ get_main_keyboard(): Berhasil")
        
        kb = keyboards.service_categories()
        print("  ✅ service_categories(): Berhasil")
        
    except Exception as e:
        print(f"  ❌ Keyboard: Gagal - {str(e)}")
    
    print()

if __name__ == "__main__":
    print("🔧 Memulai pengujian fungsi-fungsi penting AzkuraVerify...\n")
    
    test_imports()
    test_verification_services()
    test_handlers()
    test_database_connection()
    test_config()
    test_keyboards()
    
    print("✅ Pengujian selesai!")