# YouTube Config
from services.utils.universities import get_weighted_university

PROGRAM_ID = '67c8c14f5f17a83b745e3f82' # YouTube Student Program ID (Placeholder - usually dynamic)
SHEERID_BASE_URL = 'https://services.sheerid.com'
MAX_FILE_SIZE = 1 * 1024 * 1024

def get_random_school():
    return get_weighted_university()