
import random
from typing import Tuple

MALE_FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian",
    "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan",
    "Budi", "Eko", "Dwi", "Agus", "Hendra", "Rizky", "Bayu", "Aditya", "Fajar"
]

FEMALE_FIRST_NAMES = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy", "Carol",
    "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura",
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia",
    "Siti", "Sri", "Nur", "Dewi", "Putri", "Indah", "Rina", "Ayu", "Lestari"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Turner", "Phillips", "Evans", "Parker", "Edwards",
    "Santoso", "Wijaya", "Saputra", "Hidayat", "Nugroho", "Pratama", "Kusuma", "Wibowo"
]

def generate_name(gender: str = None) -> Tuple[str, str]:
    if gender == "male":
        first = random.choice(MALE_FIRST_NAMES)
    elif gender == "female":
        first = random.choice(FEMALE_FIRST_NAMES)
    else:
        # Fallback if no gender specified
        all_names = MALE_FIRST_NAMES + FEMALE_FIRST_NAMES
        first = random.choice(all_names)
        
    return first, random.choice(LAST_NAMES)
