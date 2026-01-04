# Perplexity Config (Groningen Strategy)

PROGRAM_ID = '67c8c14f5f17a83b745e3f82' # Common Program ID, usually parsed from URL
SHEERID_BASE_URL = 'https://services.sheerid.com'

# Strategy: University of Groningen
# Requires NL IP for best results
GRONINGEN = {
    "id": 291085,
    "idExtended": "291085",
    "name": "University of Groningen",
    "domain": "rug.nl",
    "country": "NL"
}

def get_groningen_school():
    return GRONINGEN
