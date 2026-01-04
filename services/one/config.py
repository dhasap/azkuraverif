# Gemini One Config
from services.utils.universities import get_weighted_university, UNIVERSITIES

PROGRAM_ID = '67c8c14f5f17a83b745e3f82' # Gemini Program ID
SHEERID_BASE_URL = 'https://services.sheerid.com'
MAX_FILE_SIZE = 1 * 1024 * 1024

# Default School: Pennsylvania State University-Main Campus
DEFAULT_SCHOOL_ID = '2565'

# Convert global list to dict for compatibility
SCHOOLS = {str(u['id']): {**u, 'idExtended': str(u['id'])} for u in UNIVERSITIES}

def get_random_school():
    return get_weighted_university()