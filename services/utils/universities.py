# Global University List for Student Verification
# Curated list of high-success universities (Weighted)
# Source: SheerID-Verification-Tool

UNIVERSITIES = [
    # =========== USA - HIGH PRIORITY (15 schools) ===========
    {"id": 2565, "name": "Pennsylvania State University-Main Campus", "domain": "psu.edu", "weight": 100},
    {"id": 3499, "name": "University of California, Los Angeles", "domain": "ucla.edu", "weight": 98},
    {"id": 3491, "name": "University of California, Berkeley", "domain": "berkeley.edu", "weight": 97},
    {"id": 1953, "name": "Massachusetts Institute of Technology", "domain": "mit.edu", "weight": 95},
    {"id": 3113, "name": "Stanford University", "domain": "stanford.edu", "weight": 95},
    {"id": 2285, "name": "New York University", "domain": "nyu.edu", "weight": 96},
    {"id": 1426, "name": "Harvard University", "domain": "harvard.edu", "weight": 92},
    {"id": 698, "name": "Columbia University", "domain": "columbia.edu", "weight": 92},
    {"id": 3568, "name": "University of Michigan", "domain": "umich.edu", "weight": 95},
    {"id": 3686, "name": "University of Texas at Austin", "domain": "utexas.edu", "weight": 94},
    {"id": 378, "name": "Arizona State University", "domain": "asu.edu", "weight": 93},
    {"id": 3521, "name": "University of Florida", "domain": "ufl.edu", "weight": 91},
    {"id": 1217, "name": "Georgia Institute of Technology", "domain": "gatech.edu", "weight": 90},
    {"id": 602, "name": "Carnegie Mellon University", "domain": "cmu.edu", "weight": 89},
    {"id": 2506, "name": "Ohio State University", "domain": "osu.edu", "weight": 88},
    
    # =========== UK (5 schools) ===========
    {"id": 273409, "name": "University of Oxford", "domain": "ox.ac.uk", "weight": 88},
    {"id": 273378, "name": "University of Cambridge", "domain": "cam.ac.uk", "weight": 88},
    {"id": 273294, "name": "Imperial College London", "domain": "imperial.ac.uk", "weight": 85},
    {"id": 273319, "name": "University College London", "domain": "ucl.ac.uk", "weight": 84},
    {"id": 273381, "name": "University of Edinburgh", "domain": "ed.ac.uk", "weight": 82},

    # =========== CANADA (3 schools) ===========
    {"id": 328355, "name": "University of Toronto", "domain": "utoronto.ca", "weight": 88},
    {"id": 4782066, "name": "McGill University", "domain": "mcgill.ca", "weight": 85},
    {"id": 328315, "name": "University of British Columbia", "domain": "ubc.ca", "weight": 86},
]

def get_weighted_university():
    """Select a university based on weight"""
    import random
    
    weights = [u["weight"] for u in UNIVERSITIES]
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    
    for uni in UNIVERSITIES:
        cumulative += uni["weight"]
        if r <= cumulative:
            # Ensure format compatibility
            return {
                "id": uni["id"],
                "idExtended": str(uni["id"]),
                "name": uni["name"],
                "domain": uni["domain"],
                "country": "US" # Defaulting for generator logic
            }
    
    # Fallback
    u = UNIVERSITIES[0]
    return {"id": u["id"], "idExtended": str(u["id"]), "name": u["name"], "domain": u["domain"], "country": "US"}
