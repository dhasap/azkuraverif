# Global University List for Student Verification
# Curated list of high-success universities (Weighted)
# Source: SheerID-Verification-Tool Reference

UNIVERSITIES = [
    # =========== VIETNAM - FULLY SUPPORTED ===========
    {"id": 588731, "name": "Hanoi University of Science and Technology", "domain": "hust.edu.vn", "weight": 98},
    {"id": 10066238, "name": "VNU University of Engineering and Technology", "domain": "uet.vnu.edu.vn", "weight": 96},
    {"id": 588738, "name": "VNU University of Information Technology", "domain": "uit.edu.vn", "weight": 94},
    {"id": 588772, "name": "FPT University", "domain": "fpt.edu.vn", "weight": 97},
    {"id": 588608, "name": "Posts and Telecommunications Institute of Technology", "domain": "ptit.edu.vn", "weight": 92},
    {"id": 10066240, "name": "Vietnam National University Ho Chi Minh City", "domain": "vnuhcm.edu.vn", "weight": 95},
    {"id": 588736, "name": "Ho Chi Minh City University of Technology", "domain": "hcmut.edu.vn", "weight": 93},
    {"id": 588607, "name": "Foreign Trade University", "domain": "ftu.edu.vn", "weight": 90},
    
    # =========== INDONESIA - FULLY SUPPORTED ===========
    {"id": 10008577, "name": "University of Indonesia", "domain": "ui.ac.id", "weight": 90},
    {"id": 10008584, "name": "Institut Teknologi Bandung", "domain": "itb.ac.id", "weight": 88},
    {"id": 10008579, "name": "Gadjah Mada University", "domain": "ugm.ac.id", "weight": 87},
    {"id": 10008589, "name": "Institut Teknologi Sepuluh Nopember", "domain": "its.ac.id", "weight": 86},
    {"id": 10008591, "name": "Bina Nusantara University", "domain": "binus.ac.id", "weight": 85},
    {"id": 10008593, "name": "Telkom University", "domain": "telkomuniversity.ac.id", "weight": 84},
    
    # =========== USA - HIGH PRIORITY ===========
    {"id": 2565, "name": "Pennsylvania State University-Main Campus", "domain": "psu.edu", "weight": 100},
    {"id": 3499, "name": "University of California, Los Angeles", "domain": "ucla.edu", "weight": 98},
    {"id": 3491, "name": "University of California, Berkeley", "domain": "berkeley.edu", "weight": 97},
    {"id": 2285, "name": "New York University", "domain": "nyu.edu", "weight": 96},
    {"id": 3568, "name": "University of Michigan", "domain": "umich.edu", "weight": 95},
    {"id": 378, "name": "Arizona State University", "domain": "asu.edu", "weight": 94},
    {"id": 3521, "name": "University of Florida", "domain": "ufl.edu", "weight": 93},
    
    # =========== INDIA - FULLY SUPPORTED ===========
    {"id": 10007277, "name": "Indian Institute of Technology Delhi", "domain": "iitd.ac.in", "weight": 95},
    {"id": 10007303, "name": "Indian Institute of Technology Bombay", "domain": "iitb.ac.in", "weight": 94},
    {"id": 3827577, "name": "University of Delhi", "domain": "du.ac.in", "weight": 92},
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
                "country": "US" if ".edu" in uni["domain"] and ".vn" not in uni["domain"] else "INTL"
            }
    
    u = UNIVERSITIES[0]
    return {"id": u["id"], "idExtended": str(u["id"]), "name": u["name"], "domain": u["domain"]}