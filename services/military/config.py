# Konfigurasi Verifikasi Military SheerID

# Konfigurasi SheerID API
# Program ID bisa dinamis dari URL, tapi kita bisa set default jika ada
PROGRAM_ID = '67c8c14f5f17a83b745e3f82' # Placeholder, usually parsed from URL
SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# Batas ukuran file
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Data Militer (SheerID Internal Codes)
MILITARY_STATUSES = [
    'MILITARY_VETERAN_RETIREE', 
    'ACTIVE_DUTY', 
    'RESERVIST_NATIONAL_GUARD'
]

MILITARY_BRANCHES = [
    'ARMY', 'NAVY', 'AIR_FORCE', 'MARINES', 'COAST_GUARD', 'SPACE_FORCE',
    'ARMY_NATIONAL_GUARD', 'AIR_NATIONAL_GUARD', 'ARMY_RESERVE', 'NAVY_RESERVE',
    'AIR_FORCE_RESERVE', 'MARINE_CORPS_RESERVE', 'COAST_GUARD_RESERVE'
]

# Default (Veteran + Army paling umum & sukses)
DEFAULT_STATUS = 'MILITARY_VETERAN_RETIREE'
DEFAULT_BRANCH = 'ARMY'
