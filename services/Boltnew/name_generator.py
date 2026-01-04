"""Bolt.new Teacher Name & Data Generator
Updated for teacher demographics (Age 25-55)
"""
import random
from datetime import datetime

class NameGenerator:
    """English Name Generator"""
    
    # Using more mature/professional sounding names
    FIRST_NAMES = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
        "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
        "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
    ]
    
    @classmethod
    def generate(cls):
        first = random.choice(cls.FIRST_NAMES)
        last = random.choice(cls.LAST_NAMES)
        return {
            'first_name': first,
            'last_name': last,
            'full_name': f"{first} {last}"
        }

def generate_email(school_domain='psu.edu'):
    """Generate professional university email"""
    name = NameGenerator.generate()
    first = name['first_name'][0].lower()
    last = name['last_name'].lower()
    num = random.randint(10, 99)
    return f"{first}{last}{num}@{school_domain}"

def generate_birth_date():
    """
    Generate teacher age (25-55 years old)
    Unlike students (18-24), teachers must be older.
    """
    current_year = datetime.now().year
    year = random.randint(current_year - 55, current_year - 25) # e.g., 1969 - 1999
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"