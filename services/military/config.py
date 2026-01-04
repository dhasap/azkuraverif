# SheerID Military Configuration
# Based on ChatGPT Military Verification Blueprint

# ChatGPT Military Program ID (Note: You must ensure this is the correct ID for ChatGPT)
# If this is for a different program, please update it.
PROGRAM_ID = '67c8c14f5f17a83b745e3f82' 

SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# Organization Data (Directly from Blueprint)
# Using hardcoded IDs is safer than searching
ORGANIZATIONS = {
    'Army': {
        "id": 4070,
        "idExtended": "4070",
        "name": "Army",
        "country": "US",
        "type": "MILITARY"
    },
    'Air Force': {
        "id": 4073,
        "idExtended": "4073",
        "name": "Air Force",
        "country": "US",
        "type": "MILITARY"
    },
    'Navy': {
        "id": 4072,
        "idExtended": "4072",
        "name": "Navy",
        "country": "US",
        "type": "MILITARY"
    },
    'Marine Corps': {
        "id": 4071,
        "idExtended": "4071",
        "name": "Marine Corps",
        "country": "US",
        "type": "MILITARY"
    },
    'Coast Guard': {
        "id": 4074,
        "idExtended": "4074",
        "name": "Coast Guard",
        "country": "US",
        "type": "MILITARY"
    },
    'Space Force': {
        "id": 4544268,
        "idExtended": "4544268",
        "name": "Space Force",
        "country": "US",
        "type": "MILITARY"
    }
}

# Mapping user friendly names to keys above
BRANCH_ALIASES = {
    'ARMY': 'Army',
    'NAVY': 'Navy',
    'AIR_FORCE': 'Air Force',
    'MARINES': 'Marine Corps',
    'MARINE': 'Marine Corps',
    'COAST_GUARD': 'Coast Guard',
    'SPACE_FORCE': 'Space Force'
}

DEFAULT_BRANCH = 'Army'