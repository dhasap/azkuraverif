import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import libsql_experimental as libsql
from dotenv import load_dotenv
import config  # Import config untuk reward

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TursoDatabase:
    """Manajemen Database Turso (LibSQL) untuk Telegram Bot"""

    def __init__(self):
        self.url = os.getenv("TURSO_DATABASE_URL")
        self.token = os.getenv("TURSO_AUTH_TOKEN")
        
        if not self.url or not self.token:
            logger.warning("TURSO_DATABASE_URL atau TURSO_AUTH_TOKEN belum diset di .env")

        self.init_db()

    def get_connection(self):
        """Membuka koneksi ke Turso"""
        # Jika tidak ada URL atau token, gunakan database lokal
        if not self.url or not self.token:
            return libsql.connect(database="file:local.db")
        return libsql.connect(database=self.url, auth_token=self.token)

    def init_db(self):
        """Inisialisasi tabel jika belum ada"""
        conn = self.get_connection()
        try:
            # Tabel Users (Telegram ID sebagai Primary Key)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    balance INTEGER DEFAULT 0,
                    is_blocked INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_checkin TIMESTAMP NULL
                )
            """)

            # Update Schema: Tambah kolom is_admin & invited_by
            try:
                conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            except Exception:
                pass 
            
            try:
                conn.execute("ALTER TABLE users ADD COLUMN invited_by INTEGER")
            except Exception:
                pass

            # Tabel Verifications
            conn.execute("""
                CREATE TABLE IF NOT EXISTS verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    service TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(telegram_id) REFERENCES users(telegram_id)
                )
            """)
            
            # ... (Tabel lain tetap sama) ...
            # Tabel Redeem Codes (Card Keys)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS card_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_code TEXT UNIQUE NOT NULL,
                    balance INTEGER NOT NULL,
                    max_uses INTEGER DEFAULT 1,
                    current_uses INTEGER DEFAULT 0,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expire_at TIMESTAMP NULL
                )
            """)

            # Tabel Usage History (Siapa redeem kode apa)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS card_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_code TEXT NOT NULL,
                    telegram_id INTEGER NOT NULL,
                    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(key_code) REFERENCES card_keys(key_code),
                    FOREIGN KEY(telegram_id) REFERENCES users(telegram_id)
                )
            """)

            # Tabel Settings (Key-Value Global Config)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            
            conn.commit()
            logger.info("Database Turso berhasil diinisialisasi.")
        except Exception as e:
            logger.error(f"Gagal inisialisasi database: {e}")
        finally:
            conn.close()

    # --- User Management ---

    def create_user(self, telegram_id: int, username: str, full_name: str, invited_by: Optional[int] = None) -> bool:
        """Mendaftarkan user baru. Return True jika user baru berhasil dibuat."""
        conn = self.get_connection()
        try:
            # Cek dulu apakah user sudah ada
            cursor = conn.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
            if cursor.fetchone():
                # User sudah ada, update info saja
                conn.execute(
                    "UPDATE users SET username = ?, full_name = ? WHERE telegram_id = ?",
                    (username, full_name, telegram_id)
                )
                conn.commit()
                return False
            
            # User baru
            initial_balance = config.REGISTER_REWARD
            conn.execute(
                """
                INSERT INTO users (telegram_id, username, full_name, balance, invited_by)
                VALUES (?, ?, ?, ?, ?)
                """,
                (telegram_id, username, full_name, initial_balance, invited_by)
            )
            
            # Beri reward ke pengundang jika ada
            if invited_by:
                conn.execute(
                    "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
                    (config.REFERRAL_REWARD, invited_by)
                )
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error create_user: {e}")
            return False
        finally:
            conn.close()

    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Mengambil data user"""
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            if row:
                # Ambil nama kolom
                cols = [desc[0] for desc in cursor.description]
                res = dict(zip(cols, row))
                # Konversi boolean
                res['is_blocked'] = bool(res.get('is_blocked', 0))
                res['is_admin'] = bool(res.get('is_admin', 0))
                return res
            return None
        except Exception as e:
            logger.error(f"Error get_user: {e}")
            return None
        finally:
            conn.close()

    def set_admin(self, telegram_id: int, status: bool = True) -> bool:
        """Set user sebagai admin"""
        conn = self.get_connection()
        try:
            val = 1 if status else 0
            conn.execute("UPDATE users SET is_admin = ? WHERE telegram_id = ?", (val, telegram_id))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error set_admin: {e}")
            return False
        finally:
            conn.close()

    def get_all_users(self) -> List[int]:
        """Ambil semua ID user (untuk broadcast)"""
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT telegram_id FROM users")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error get_all_users: {e}")
            return []
        finally:
            conn.close()

    def get_stats(self) -> Dict:
        """Ambil statistik global"""
        conn = self.get_connection()
        try:
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            total_verif = conn.execute("SELECT COUNT(*) FROM verifications").fetchone()[0]
            success_verif = conn.execute("SELECT COUNT(*) FROM verifications WHERE status='success'").fetchone()[0]
            return {
                "users": total_users,
                "verifications": total_verif,
                "success": success_verif
            }
        except Exception as e:
            logger.error(f"Error get_stats: {e}")
            return {"users": 0, "verifications": 0, "success": 0}
        finally:
            conn.close()

    # --- Settings ---
    
    def set_setting(self, key: str, value: str):
        conn = self.get_connection()
        try:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error set_setting: {e}")
        finally:
            conn.close()

    def get_setting(self, key: str, default: str = None) -> str:
        conn = self.get_connection()
        try:
            cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
        except Exception as e:
            logger.error(f"Error get_setting: {e}")
            return default
        finally:
            conn.close()

    def add_balance(self, telegram_id: int, amount: int) -> bool:
        """Menambah saldo user"""
        conn = self.get_connection()
        try:
            conn.execute(
                "UPDATE users SET balance = balance + ? WHERE telegram_id = ?",
                (amount, telegram_id)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error add_balance: {e}")
            return False
        finally:
            conn.close()

    def deduct_balance(self, telegram_id: int, amount: int) -> bool:
        """Mengurangi saldo user (cek cukup/tidak)"""
        user = self.get_user(telegram_id)
        if not user or user["balance"] < amount:
            return False

        conn = self.get_connection()
        try:
            conn.execute(
                "UPDATE users SET balance = balance - ? WHERE telegram_id = ?",
                (amount, telegram_id)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error deduct_balance: {e}")
            return False
        finally:
            conn.close()

    # --- Verification Logging ---

    def add_verification(self, telegram_id: int, service: str, status: str, data: str = ""):
        """Mencatat histori verifikasi"""
        conn = self.get_connection()
        try:
            conn.execute(
                """
                INSERT INTO verifications (telegram_id, service, status, data)
                VALUES (?, ?, ?, ?)
                """,
                (telegram_id, service, status, data)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error add_verification: {e}")
        finally:
            conn.close()

    # --- Redeem Code System ---

    def create_card(self, key_code: str, balance: int, max_uses: int = 1):
        """Admin membuat kode redeem"""
        conn = self.get_connection()
        try:
            conn.execute(
                "INSERT INTO card_keys (key_code, balance, max_uses) VALUES (?, ?, ?)",
                (key_code, balance, max_uses)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error create_card: {e}")
            return False
        finally:
            conn.close()

    def redeem_card(self, telegram_id: int, key_code: str) -> Dict:
        """User mengklaim kode redeem"""
        conn = self.get_connection()
        try:
            # 1. Cek validitas kode
            cursor = conn.execute("SELECT * FROM card_keys WHERE key_code = ?", (key_code,))
            card = cursor.fetchone() # (id, key, bal, max, curr, creator, created, expire)
            
            if not card:
                return {"success": False, "message": "Kode tidak ditemukan."}
            
            # Map tuple to vars for clarity
            balance_reward = card[2]
            max_uses = card[3]
            current_uses = card[4]
            expire_at = card[7]

            if current_uses >= max_uses:
                return {"success": False, "message": "Kode sudah habis terpakai."}
            
            if expire_at and datetime.now().isoformat() > expire_at:
                return {"success": False, "message": "Kode sudah kadaluarsa."}

            # 2. Cek apakah user sudah pernah redeem kode ini
            cursor = conn.execute(
                "SELECT COUNT(*) FROM card_usage WHERE key_code = ? AND telegram_id = ?",
                (key_code, telegram_id)
            )
            if cursor.fetchone()[0] > 0:
                return {"success": False, "message": "Anda sudah pernah menggunakan kode ini."}

            # 3. Eksekusi Redeem (Update card, Insert usage, Update user)
            # Karena LibSQL HTTP tidak support transaction block komplex dengan mudah di python driver dasar,
            # kita lakukan sequential update. Idealnya ini dalam satu transaction.
            
            conn.execute("UPDATE card_keys SET current_uses = current_uses + 1 WHERE key_code = ?", (key_code,))
            conn.execute("INSERT INTO card_usage (key_code, telegram_id) VALUES (?, ?)", (key_code, telegram_id))
            conn.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (balance_reward, telegram_id))
            
            conn.commit()
            return {"success": True, "amount": balance_reward}

        except Exception as e:
            logger.error(f"Error redeem_card: {e}")
            return {"success": False, "message": "Terjadi kesalahan sistem."}
        finally:
            conn.close()

    def get_transaction_history(self, telegram_id: int, limit: int = 10) -> List[Dict]:
        """Mengambil 10 riwayat transaksi terakhir (Verifikasi & Redeem)"""
        conn = self.get_connection()
        try:
            # Query Union untuk menggabungkan log verifikasi dan redeem voucher
            query = """
                SELECT 'verify' as type, service as description, created_at, status 
                FROM verifications 
                WHERE telegram_id = ?
                
                UNION ALL
                
                SELECT 'redeem' as type, key_code as description, used_at as created_at, 'success' as status 
                FROM card_usage 
                WHERE telegram_id = ?
                
                ORDER BY created_at DESC 
                LIMIT ?
            """
            cursor = conn.execute(query, (telegram_id, telegram_id, limit))
            cols = [desc[0] for desc in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error get_transaction_history: {e}")
            return []
        finally:
            conn.close()

# Singleton instance
db = TursoDatabase()
