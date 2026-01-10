# YouTube Config
from .universities import UNIVERSITIES
import random

# Program ID from working reference script
PROGRAM_ID = '67c8c14f5f17a83b745e3f82'
SHEERID_BASE_URL = 'https://services.sheerid.com'
MAX_FILE_SIZE = 1 * 1024 * 1024

# Default School: Pennsylvania State University-Main Campus
DEFAULT_SCHOOL_ID = '2565'

# Convert global list to dict for compatibility
SCHOOLS = {str(u['id']): {**u, 'idExtended': str(u['id'])} for u in UNIVERSITIES}

def get_random_school():
    """Select a university based on weight"""
    weights = [u["weight"] for u in UNIVERSITIES]
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    
    for uni in UNIVERSITIES:
        cumulative += uni["weight"]
        if r <= cumulative:
            return {**uni, "idExtended": str(uni["id"])}
    
    u = UNIVERSITIES[0]
    return {**u, "idExtended": str(u["id"])}