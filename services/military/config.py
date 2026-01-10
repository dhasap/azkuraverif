# SheerID Military Configuration
# Based on ChatGPT Military Verification Blueprint
# Updated with source-code organization IDs

# ChatGPT Military Program ID (Note: You must ensure this is the correct ID for ChatGPT)
# If this is for a different program, please update it.
PROGRAM_ID = '690415d58971e73ca187d8c9'

SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# Organization Data (Updated from source-code)
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
    },
    'Army National Guard': {
        "id": 4075,
        "idExtended": "4075",
        "name": "Army National Guard",
        "country": "US",
        "type": "MILITARY"
    },
    'Army Reserve': {
        "id": 4076,
        "idExtended": "4076",
        "name": "Army Reserve",
        "country": "US",
        "type": "MILITARY"
    },
    'Air National Guard': {
        "id": 4079,
        "idExtended": "4079",
        "name": "Air National Guard",
        "country": "US",
        "type": "MILITARY"
    },
    'Air Force Reserve': {
        "id": 4080,
        "idExtended": "4080",
        "name": "Air Force Reserve",
        "country": "US",
        "type": "MILITARY"
    },
    'Navy Reserve': {
        "id": 4078,
        "idExtended": "4078",
        "name": "Navy Reserve",
        "country": "US",
        "type": "MILITARY"
    },
    'Marine Corps Reserve': {
        "id": 4077,
        "idExtended": "4077",
        "name": "Marine Corps Forces Reserve",
        "country": "US",
        "type": "MILITARY"
    },
    'Coast Guard Reserve': {
        "id": 4081,
        "idExtended": "4081",
        "name": "Coast Guard Reserve",
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
    'SPACE_FORCE': 'Space Force',
    'ARMY_NATIONAL_GUARD': 'Army National Guard',
    'ARMY_RESERVE': 'Army Reserve',
    'AIR_NATIONAL_GUARD': 'Air National Guard',
    'AIR_FORCE_RESERVE': 'Air Force Reserve',
    'NAVY_RESERVE': 'Navy Reserve',
    'MARINE_CORPS_RESERVE': 'Marine Corps Reserve',
    'COAST_GUARD_RESERVE': 'Coast Guard Reserve'
}

DEFAULT_BRANCH = 'Army'