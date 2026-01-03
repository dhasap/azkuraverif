# Konfigurasi Verifikasi Military SheerID

# Konfigurasi SheerID API
PROGRAM_ID = '67c8c14f5f17a83b745e3f82' 
SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# Data Militer (Mapping Nama ke ID Resmi SheerID)
# ID ini adalah ID standar global SheerID untuk Cabang Militer
MILITARY_BRANCH_IDS = {
    'Air Force': 1261,
    'Air Force Reserve': 1270,
    'Air National Guard': 1264,
    'Army': 1259,
    'Army National Guard': 1263,
    'Army Reserve': 1266,
    'Coast Guard': 1262,
    'Coast Guard Reserve': 1271,
    'Marine Corps': 1260,
    'Marine Corps Forces Reserve': 1269,
    'Navy': 1258,
    'Navy Reserve': 1267,
    'Space Force': 13161
}

# Status Militer
MILITARY_STATUS_MAP = {
    'Military Veteran or Retiree': 'VETERAN',
    'Active Duty': 'ACTIVE_DUTY',
    'Reservist or National Guard': 'RESERVIST'
}

# Default untuk ChatGPT Veteran
DEFAULT_STATUS = 'VETERAN'
DEFAULT_BRANCH = 'Army'
