# YouTube Config
from services.utils.universities import get_weighted_university

# Program ID from working reference script
PROGRAM_ID = '67c8c14f5f17a83b745e3f82'
SHEERID_BASE_URL = 'https://services.sheerid.com'
MAX_FILE_SIZE = 1 * 1024 * 1024

# Default School: Pennsylvania State University-Main Campus (ID verified from reference)
DEFAULT_SCHOOL_ID = '2565'

SCHOOLS = {
    '2565': {
        'id': 2565,
        'idExtended': '2565',
        'name': 'Pennsylvania State University-Main Campus',
        'domain': 'psu.edu'
    },
    '3499': {
        'id': 3499,
        'idExtended': '3499',
        'name': 'University of California, Los Angeles',
        'domain': 'ucla.edu'
    },
    '3568': {
        'id': 3568,
        'idExtended': '3568',
        'name': 'University of Michigan',
        'domain': 'umich.edu'
    }
}

def get_random_school():
    # Fallback to internal list if needed, or implement weighted logic later
    return SCHOOLS[DEFAULT_SCHOOL_ID]