# YouTube Config
from services.utils.universities import get_weighted_university

# Program ID extracted from YouTube Student SheerID Page
PROGRAM_ID = '633f45d7295c0551ab43b87a' 
SHEERID_BASE_URL = 'https://services.sheerid.com'
MAX_FILE_SIZE = 1 * 1024 * 1024

# Default School Configuration
DEFAULT_SCHOOL_ID = '21415' # PSU

SCHOOLS = {
    '21415': {
        'id': 21415,
        'idExtended': '21415',
        'name': 'Pennsylvania State University',
        'domain': 'psu.edu'
    },
    '20688': {
        'id': 20688,
        'idExtended': '20688',
        'name': 'Ohio State University',
        'domain': 'osu.edu'
    },
    '23068': {
        'id': 23068,
        'idExtended': '23068',
        'name': 'University of Southern California',
        'domain': 'usc.edu'
    }
}

def get_random_school():
    return get_weighted_university()