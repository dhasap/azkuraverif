# SheerID K12 Teacher Verification Configuration
# Strategy: Target specific "K12" type schools for high auto-approval rate

PROGRAM_ID = '68d47554aa292d20b9bec8f7'
SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# File size limit
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# Curated list of high-success K12 schools (US Only)
# Source: SheerID-Verification-Tool/k12-verify-tool
SCHOOLS = {
    # NYC Specialized
    "155694": {"id": 155694, "name": "Stuyvesant High School", "city": "New York", "state": "NY", "type": "K12", "weight": 100},
    "156251": {"id": 156251, "name": "Bronx High School Of Science", "city": "Bronx", "state": "NY", "type": "K12", "weight": 98},
    "157582": {"id": 157582, "name": "Brooklyn Technical High School", "city": "Brooklyn", "state": "NY", "type": "K12", "weight": 95},
    "155770": {"id": 155770, "name": "Staten Island Technical High School", "city": "Staten Island", "state": "NY", "type": "K12", "weight": 90},
    
    # Chicago Selective
    "3521141": {"id": 3521141, "name": "Walter Payton College Preparatory High School", "city": "Chicago", "state": "IL", "type": "K12", "weight": 95},
    "3521074": {"id": 3521074, "name": "Whitney M Young Magnet High School", "city": "Chicago", "state": "IL", "type": "K12", "weight": 92},
    
    # Virginia/DC STEM
    "3704245": {"id": 3704245, "name": "Thomas Jefferson High School For Science And Technology", "city": "Alexandria", "state": "VA", "type": "K12", "weight": 100},
    
    # California Elite
    "3539252": {"id": 3539252, "name": "Gretchen Whitney High School", "city": "Cerritos", "state": "CA", "type": "K12", "weight": 95},
    "262338": {"id": 262338, "name": "Lowell High School", "city": "San Francisco", "state": "CA", "type": "K12", "weight": 90},
    
    # BASIS Charter (High Auto-Pass)
    "3536914": {"id": 3536914, "name": "BASIS Scottsdale", "city": "Scottsdale", "state": "AZ", "type": "K12", "weight": 90},
    "250527": {"id": 250527, "name": "BASIS Tucson North", "city": "Tucson", "state": "AZ", "type": "K12", "weight": 88},
    
    # Top 50 US
    "202063": {"id": 202063, "name": "Signature School Inc", "city": "Evansville", "state": "IN", "type": "K12", "weight": 95},
    "3506727": {"id": 3506727, "name": "Loveless Academic Magnet Program High School", "city": "Montgomery", "state": "AL", "type": "K12", "weight": 90}
}

DEFAULT_SCHOOL_ID = "3704245"  # Thomas Jefferson HS (Very reliable)