#!/usr/bin/env python3
"""
Script untuk memperbaiki struktur database jika ada kolom yang hilang
"""

import libsql_experimental as libsql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_database():
    """Perbaiki struktur database"""
    url = os.getenv("TURSO_DATABASE_URL", "file:local.db")
    token = os.getenv("TURSO_AUTH_TOKEN")
    
    # Jika tidak ada token, gunakan database lokal
    if not token:
        conn = libsql.connect(database="file:local.db")
    else:
        conn = libsql.connect(database=url, auth_token=token)
    
    try:
        # Cek dan tambahkan kolom is_admin jika belum ada
        try:
            conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            print("✅ Kolom 'is_admin' berhasil ditambahkan")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ Kolom 'is_admin' sudah ada")
            else:
                print(f"⚠️ Error saat menambahkan kolom 'is_admin': {e}")

        # Cek dan tambahkan kolom invited_by jika belum ada
        try:
            conn.execute("ALTER TABLE users ADD COLUMN invited_by INTEGER")
            print("✅ Kolom 'invited_by' berhasil ditambahkan")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ Kolom 'invited_by' sudah ada")
            else:
                print(f"⚠️ Error saat menambahkan kolom 'invited_by': {e}")

        # Cek dan tambahkan kolom last_checkin jika belum ada
        try:
            conn.execute("ALTER TABLE users ADD COLUMN last_checkin TIMESTAMP NULL")
            print("✅ Kolom 'last_checkin' berhasil ditambahkan")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("ℹ️ Kolom 'last_checkin' sudah ada")
            else:
                print(f"⚠️ Error saat menambahkan kolom 'last_checkin': {e}")

        conn.commit()
        print("\n✅ Perbaikan struktur database selesai")
        
    except Exception as e:
        print(f"❌ Error saat memperbaiki database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 Memulai perbaikan struktur database...")
    fix_database()