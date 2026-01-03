"""Generator Nama & Data Militer"""
import random
from datetime import datetime, timedelta

class NameGenerator:
    """Generator Nama Bahasa Inggris"""
    
    ROOTS = {
        'prefixes': ['Al', 'Bri', 'Car', 'Dan', 'El', 'Fer', 'Gar', 'Har', 'Jes', 'Kar', 
                    'Lar', 'Mar', 'Nor', 'Par', 'Quin', 'Ros', 'Sar', 'Tar', 'Val', 'Wil'],
        'middles': ['an', 'en', 'in', 'on', 'ar', 'er', 'or', 'ur', 'al', 'el', 
                   'il', 'ol', 'am', 'em', 'im', 'om', 'ay', 'ey', 'oy', 'ian'],
        'suffixes': ['ton', 'son', 'man', 'ley', 'field', 'ford', 'wood', 'stone', 'worth', 'berg',
                    'stein', 'bach', 'heim', 'gard', 'land', 'wick', 'shire', 'dale', 'brook', 'ridge'],
        'name_roots': ['Alex', 'Bern', 'Crist', 'Dav', 'Edw', 'Fred', 'Greg', 'Henr', 'Ivan', 'John',
                      'Ken', 'Leon', 'Mich', 'Nick', 'Oliv', 'Paul', 'Rich', 'Step', 'Thom', 'Will'],
        'name_endings': ['a', 'e', 'i', 'o', 'y', 'ie', 'ey', 'an', 'en', 'in', 
                        'on', 'er', 'ar', 'or', 'el', 'al', 'iel', 'ael', 'ine', 'lyn']
    }
    
    PATTERNS = {
        'first_name': [
            ['prefix', 'ending'],
            ['name_root', 'ending'],
            ['prefix', 'middle', 'ending'],
            ['name_root', 'middle', 'ending']
        ],
        'last_name': [
            ['prefix', 'suffix'],
            ['name_root', 'suffix'],
            ['prefix', 'middle', 'suffix'],
            ['compound']
        ]
    }
    
    @classmethod
    def _generate_component(cls, pattern):
        components = []
        for part in pattern:
            if part == 'prefix':
                component = random.choice(cls.ROOTS['prefixes'])
            elif part == 'middle':
                component = random.choice(cls.ROOTS['middles'])
            elif part == 'suffix':
                component = random.choice(cls.ROOTS['suffixes'])
            elif part == 'name_root':
                component = random.choice(cls.ROOTS['name_roots'])
            elif part == 'ending':
                component = random.choice(cls.ROOTS['name_endings'])
            elif part == 'compound':
                part1 = random.choice(cls.ROOTS['prefixes'])
                part2 = random.choice(cls.ROOTS['suffixes'])
                component = part1 + part2
            else:
                component = ''
            
            components.append(component)
        
        return ''.join(components)
    
    @classmethod
    def generate(cls):
        first_name = cls._generate_component(random.choice(cls.PATTERNS['first_name'])).capitalize()
        last_name = cls._generate_component(random.choice(cls.PATTERNS['last_name'])).capitalize()
        return {
            'first_name': first_name,
            'last_name': last_name,
            'full_name': f"{first_name} {last_name}"
        }

def generate_email(first_name, last_name):
    """Membuat email umum (Gmail/Yahoo/etc)"""
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    sep = random.choice(['.', '_', ''])
    num = random.randint(10, 999)
    domain = random.choice(domains)
    return f"{first_name.lower()}{sep}{last_name.lower()}{num}@{domain}"

def generate_birth_date():
    """Usia Veteran (biasanya lebih tua, misal 25-50 tahun)"""
    # Tahun sekarang - (25 s/d 50)
    current_year = datetime.now().year
    year = current_year - random.randint(25, 50)
    month = str(random.randint(1, 12)).zfill(2)
    day = str(random.randint(1, 28)).zfill(2)
    return f"{year}-{month}-{day}"

def generate_discharge_date():
    """Tanggal Discharge (misal 1-5 tahun lalu)"""
    days_ago = random.randint(365, 365*5)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")
