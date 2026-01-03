# Konfigurasi Verifikasi Military SheerID

# Konfigurasi SheerID API
PROGRAM_ID = '67c8c14f5f17a83b745e3f82' 
SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# Data Militer (Mapping sesuai Pilihan Web SheerID)
MILITARY_STATUSES = {
    'Active Duty': 'ACTIVE_DUTY',
    'Military Veteran or Retiree': 'VETERAN',
    'Reservist or National Guard': 'RESERVIST'
}

MILITARY_BRANCHES = {
    'Air Force': 'AIR_FORCE',
    'Air Force Reserve': 'AIR_FORCE_RESERVE',
    'Air National Guard': 'AIR_NATIONAL_GUARD',
    'Army': 'ARMY',
    'Army National Guard': 'ARMY_NATIONAL_GUARD',
    'Army Reserve': 'ARMY_RESERVE',
    'Coast Guard': 'COAST_GUARD',
    'Coast Guard Reserve': 'COAST_GUARD_RESERVE',
    'Marine Corps': 'MARINES',
    'Marine Corps Forces Reserve': 'MARINE_CORPS_RESERVE',
    'Navy': 'NAVY',
    'Navy Reserve': 'NAVY_RESERVE',
    'Space Force': 'SPACE_FORCE'
}

# Default untuk ChatGPT Veteran
DEFAULT_STATUS = 'VETERAN'
DEFAULT_BRANCH = 'ARMY'