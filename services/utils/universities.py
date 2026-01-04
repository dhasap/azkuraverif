# Global University List for Student Verification
# Restricted to US Universities for maximum compatibility with generic Program IDs
# Source: SheerID-Verification-Tool

UNIVERSITIES = [
    # =========== USA - HIGH PRIORITY (Most likely to work) ===========
    {"id": 2565, "name": "Pennsylvania State University-Main Campus", "domain": "psu.edu", "weight": 100},
    {"id": 3499, "name": "University of California, Los Angeles", "domain": "ucla.edu", "weight": 98},
    {"id": 3491, "name": "University of California, Berkeley", "domain": "berkeley.edu", "weight": 97},
    {"id": 2285, "name": "New York University", "domain": "nyu.edu", "weight": 96},
    {"id": 3568, "name": "University of Michigan", "domain": "umich.edu", "weight": 95},
    {"id": 378, "name": "Arizona State University", "domain": "asu.edu", "weight": 94},
    {"id": 3521, "name": "University of Florida", "domain": "ufl.edu", "weight": 93},
    {"id": 3686, "name": "University of Texas at Austin", "domain": "utexas.edu", "weight": 92},
    {"id": 1217, "name": "Georgia Institute of Technology", "domain": "gatech.edu", "weight": 91},
    {"id": 602, "name": "Carnegie Mellon University", "domain": "cmu.edu", "weight": 90},
    {"id": 2506, "name": "Ohio State University", "domain": "osu.edu", "weight": 89},
    {"id": 1953, "name": "Massachusetts Institute of Technology", "domain": "mit.edu", "weight": 88},
    {"id": 3113, "name": "Stanford University", "domain": "stanford.edu", "weight": 88},
    {"id": 1426, "name": "Harvard University", "domain": "harvard.edu", "weight": 85},
    {"id": 698, "name": "Columbia University", "domain": "columbia.edu", "weight": 85},
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
            return {
                "id": uni["id"],
                "idExtended": str(uni["id"]),
                "name": uni["name"],
                "domain": uni["domain"],
                "country": "US"
            }
    
    u = UNIVERSITIES[0]
    return {"id": u["id"], "idExtended": str(u["id"]), "name": u["name"], "domain": u["domain"], "country": "US"}
