#!/usr/bin/env python3
"""
Script untuk mengecek konsistensi semua layanan verifikasi
"""

import os
import sys
from pathlib import Path

def check_verification_services():
    """Cek semua layanan verifikasi untuk memastikan konsistensi"""
    services_dir = Path("services")
    verification_files = []
    
    # Cari semua file sheerid_verifier.py di subfolder services
    for root, dirs, files in os.walk(services_dir):
        for file in files:
            if file == "sheerid_verifier.py":
                verification_files.append(Path(root) / file)
    
    print(f"🔍 Ditemukan {len(verification_files)} layanan verifikasi:")
    
    for vf in verification_files:
        print(f"  - {vf}")
        
        # Baca file untuk memeriksa komponen penting
        with open(vf, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Cek komponen penting
        checks = {
            'SheerIDVerifier class': 'class SheerIDVerifier' in content,
            'verify method': 'def verify(' in content,
            'parse_verification_id method': 'def parse_verification_id' in content,
            'async support': 'async def' in content,
            'error handling': 'try:' in content or 'except' in content
        }
        
        print(f"    ✅ Class SheerIDVerifier: {'Ya' if checks['SheerIDVerifier class'] else 'Tidak'}")
        print(f"    ✅ Method verify: {'Ya' if checks['verify method'] else 'Tidak'}")
        print(f"    ✅ Method parse_verification_id: {'Ya' if checks['parse_verification_id method'] else 'Tidak'}")
        print(f"    ✅ Async support: {'Ya' if checks['async support'] else 'Tidak'}")
        print(f"    ✅ Error handling: {'Ya' if checks['error handling'] else 'Tidak'}")
        print()

def check_imports_consistency():
    """Cek konsistensi import di semua layanan verifikasi"""
    services_dir = Path("services")
    verification_files = []
    
    for root, dirs, files in os.walk(services_dir):
        for file in files:
            if file == "sheerid_verifier.py":
                verification_files.append(Path(root) / file)
    
    print("🔍 Mengecek konsistensi import...")
    
    for vf in verification_files:
        with open(vf, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Cek import penting
        imports = {
            'httpx': 'import httpx' in content or 'from httpx' in content,
            'logging': 'import logging' in content or 'from logging' in content,
            're': 'import re' in content or 'from re' in content,
            'anti_detect': 'from services.utils.anti_detect' in content,
            'email_client': 'from services.utils.email_client' in content
        }
        
        service_name = vf.parent.name
        print(f"  {service_name}:")
        print(f"    ✅ httpx: {'Ya' if imports['httpx'] else 'Tidak'}")
        print(f"    ✅ logging: {'Ya' if imports['logging'] else 'Tidak'}")
        print(f"    ✅ re: {'Ya' if imports['re'] else 'Tidak'}")
        print(f"    ✅ anti_detect: {'Ya' if imports['anti_detect'] else 'Tidak'}")
        print(f"    ✅ email_client: {'Ya' if imports['email_client'] else 'Tidak'}")
        print()

if __name__ == "__main__":
    print("🔧 Mengecek konsistensi layanan verifikasi...\n")
    check_verification_services()
    print("\n" + "="*50 + "\n")
    check_imports_consistency()