"""Tool Kontrol Konkurensi (Versi Optimized)

Peningkatan performa:
1. Batas konkurensi dinamis (berdasarkan beban sistem)
2. Pemisahan kontrol konkurensi untuk tipe verifikasi berbeda
3. Mendukung konkurensi lebih tinggi
4. Monitoring beban dan penyesuaian otomatis
"""
import asyncio
import logging
from typing import Dict
import psutil

logger = logging.getLogger(__name__)

# Hitung maksimum konkurensi secara dinamis
def _calculate_max_concurrency() -> int:
    """Hitung maksimum konkurensi berdasarkan resource sistem"""
    try:
        cpu_count = psutil.cpu_count() or 4
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        
        # Hitung berdasarkan CPU dan memori
        # Setiap core CPU mendukung 3-5 tugas konkurensi
        # Setiap GB memori mendukung 2 tugas konkurensi
        cpu_based = cpu_count * 4
        memory_based = int(memory_gb * 2)
        
        # Ambil nilai minimum dari keduanya, dan set batas atas-bawah
        max_concurrent = min(cpu_based, memory_based)
        max_concurrent = max(10, min(max_concurrent, 100))  # antara 10-100
        
        logger.info(
            f"Resource sistem: CPU={cpu_count}, Memory={memory_gb:.1f}GB, "
            f"Hitung konkurensi={max_concurrent}"
        )
        
        return max_concurrent
        
    except Exception as e:
        logger.warning(f"Tidak bisa mendapat info resource sistem: {e}, gunakan nilai default")
        return 20  # Nilai default

# Hitung batas konkurensi untuk setiap tipe verifikasi
_base_concurrency = _calculate_max_concurrency()

# Buat semaphore independen untuk tipe verifikasi berbeda
# Ini dapat menghindari satu tipe verifikasi memblokir tipe lain
_verification_semaphores: Dict[str, asyncio.Semaphore] = {
    "gemini_one_pro": asyncio.Semaphore(_base_concurrency // 5),
    "chatgpt_teacher_k12": asyncio.Semaphore(_base_concurrency // 5),
    "spotify_student": asyncio.Semaphore(_base_concurrency // 5),
    "youtube_student": asyncio.Semaphore(_base_concurrency // 5),
    "bolt_teacher": asyncio.Semaphore(_base_concurrency // 5),
}


def get_verification_semaphore(verification_type: str) -> asyncio.Semaphore:
    """Dapatkan semaphore untuk tipe verifikasi tertentu
    
    Args:
        verification_type: Tipe verifikasi
        
    Returns:
        asyncio.Semaphore: Semaphore yang sesuai
    """
    semaphore = _verification_semaphores.get(verification_type)
    
    if semaphore is None:
        # Tipe tidak dikenal, buat semaphore default
        semaphore = asyncio.Semaphore(_base_concurrency // 3)
        _verification_semaphores[verification_type] = semaphore
        logger.info(
            f"Buat semaphore untuk tipe verifikasi baru {verification_type}: "
            f"limit={_base_concurrency // 3}"
        )
    
    return semaphore


def get_concurrency_stats() -> Dict[str, Dict[str, int]]:
    """Dapatkan info statistik konkurensi
    
    Returns:
        dict: Info konkurensi untuk setiap tipe verifikasi
    """
    stats = {}
    for vtype, semaphore in _verification_semaphores.items():
        # Catatan: _value adalah atribut internal, mungkin berubah di versi Python berbeda
        try:
            available = semaphore._value if hasattr(semaphore, '_value') else 0
            limit = _base_concurrency // 3
            in_use = limit - available
        except Exception:
            available = 0
            limit = _base_concurrency // 3
            in_use = 0
        
        stats[vtype] = {
            'limit': limit,
            'in_use': in_use,
            'available': available,
        }
    
    return stats


async def monitor_system_load() -> Dict[str, float]:
    """Monitor beban sistem
    
    Returns:
        dict: Info beban sistem
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'concurrency_limit': _base_concurrency,
        }
    except Exception as e:
        logger.error(f"Monitor beban sistem gagal: {e}")
        return {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'concurrency_limit': _base_concurrency,
        }


def adjust_concurrency_limits(multiplier: float = 1.0):
    """Sesuaikan batas konkurensi secara dinamis
    
    Args:
        multiplier: Kelipatan penyesuaian (0.5-2.0)
    """
    global _verification_semaphores, _base_concurrency
    
    # Batasi rentang kelipatan
    multiplier = max(0.5, min(multiplier, 2.0))
    
    new_base = int(_base_concurrency * multiplier)
    new_limit = max(5, min(new_base // 3, 50))  # Setiap tipe 5-50
    
    logger.info(
        f"Sesuaikan batas konkurensi: multiplier={multiplier}, "
        f"new_base={new_base}, per_type={new_limit}"
    )
    
    # Buat semaphore baru
    for vtype in _verification_semaphores.keys():
        _verification_semaphores[vtype] = asyncio.Semaphore(new_limit)


# Task monitoring beban
_monitor_task = None

async def start_load_monitoring(interval: float = 60.0):
    """Mulai task monitoring beban
    
    Args:
        interval: Interval monitoring (detik)
    """
    global _monitor_task
    
    if _monitor_task is not None:
        return
    
    async def monitor_loop():
        while True:
            try:
                await asyncio.sleep(interval)
                
                load_info = await monitor_system_load()
                cpu = load_info['cpu_percent']
                memory = load_info['memory_percent']
                
                logger.info(
                    f"Beban sistem: CPU={cpu:.1f}%, Memory={memory:.1f}%"
                )
                
                # Sesuaikan batas konkurensi otomatis
                if cpu > 80 or memory > 85:
                    # Beban terlalu tinggi, turunkan konkurensi
                    adjust_concurrency_limits(0.7)
                    logger.warning("Beban sistem terlalu tinggi, turunkan batas konkurensi")
                elif cpu < 40 and memory < 60:
                    # Beban rendah, bisa naikkan konkurensi
                    adjust_concurrency_limits(1.2)
                    logger.info("Beban sistem rendah, naikkan batas konkurensi")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring beban exception: {e}")
    
    _monitor_task = asyncio.create_task(monitor_loop())
    logger.info(f"Monitoring beban telah dimulai: interval={interval}s")


async def stop_load_monitoring():
    """Hentikan task monitoring beban"""
    global _monitor_task
    
    if _monitor_task is not None:
        _monitor_task.cancel()
        try:
            await _monitor_task
        except asyncio.CancelledError:
            pass
        _monitor_task = None
        logger.info("Monitoring beban telah dihentikan")
