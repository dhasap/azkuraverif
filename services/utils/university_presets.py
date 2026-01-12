
import random
from datetime import datetime

def generate_ui_nim():
    """UI: 10 digit, 2 digit tahun + kode"""
    year = str(datetime.now().year)[2:]
    # Tahun masuk biasanya 1-3 tahun lalu
    entry_year = str(int(year) - random.randint(0, 3)).zfill(2)
    return f"{entry_year}{random.randint(10000000, 99999999)}"

def generate_ugm_nim():
    """UGM: YY/FC/XXXXXX/ZZZ"""
    year = str(datetime.now().year)[2:]
    entry_year = str(int(year) - random.randint(0, 3)).zfill(2)
    univ_num = random.randint(300000, 499999)
    faculty_num = random.randint(10000, 50000)
    # Mapping sederhana kode fakultas
    facs = ["TK", "PA", "KU", "PN", "PE"] 
    return f"{entry_year}/{univ_num}/{random.choice(facs)}/{faculty_num}"

def generate_itb_nim():
    """ITB: 8 digit, Kode Prodi + Tahun + Urut"""
    year = str(datetime.now().year)[2:]
    entry_year = str(int(year) - random.randint(0, 3)).zfill(2)
    prodi_code = random.randint(100, 199) # Kode prodi
    return f"{prodi_code}{entry_year}{random.randint(100, 999):03d}"

def generate_unair_nim():
    """UNAIR: 9 digit"""
    # Digit awal seringkali kode fakultas/tahun
    return f"{random.randint(1, 9)}{str(datetime.now().year)[2:]}{random.randint(100000, 999999)}"

def generate_ub_nim():
    """UB: 15 digit (biasanya) atau pola tahun"""
    # Pola umum: Tahun (2) + Kode Fak (2) + dll
    year = str(datetime.now().year)[2:]
    entry_year = str(int(year) - random.randint(0, 3)).zfill(2)
    return f"{entry_year}{random.randint(1000000000000, 9999999999999)}"

def generate_penn_id():
    """Penn State: 9 digit starting with 9"""
    return f"9{random.randint(10000000, 99999999)}"

def generate_us_id(length=9):
    return "".join([str(random.randint(0, 9)) for _ in range(length)])

UNIVERSITY_PRESETS = {
    # ================= INDONESIA =================
    10008577: { # UI
        "name": "Universitas Indonesia",
        "domain": "ui.ac.id",
        "colors": ["#FFD700", "#000000"], # Kuning Makara
        "card_title": "KARTU TANDA MAHASISWA",
        "address": "Kampus UI Depok, Jawa Barat 16424",
        "logo_file": "UI.png",
        "id_format": generate_ui_nim,
        "colleges": ["Fakultas Teknik", "Fakultas Kedokteran", "Fakultas Ekonomi & Bisnis", "Fakultas Ilmu Komputer", "Fakultas Hukum"]
    },
    10008579: { # UGM
        "name": "Universitas Gadjah Mada",
        "domain": "ugm.ac.id",
        "colors": ["#004A75", "#FFD700"], # Biru UGM
        "card_title": "KARTU MAHASISWA",
        "address": "Bulaksumur, Yogyakarta 55281",
        "logo_file": "UGM.png",
        "id_format": generate_ugm_nim,
        "colleges": ["Fakultas Teknik", "Fakultas Ekonomika dan Bisnis", "Fakultas MIPA", "Fakultas Hukum"]
    },
    10008584: { # ITB
        "name": "Institut Teknologi Bandung",
        "domain": "itb.ac.id",
        "colors": ["#2F5597", "#FFFFFF"], # Biru Ganesha
        "card_title": "KARTU TANDA MAHASISWA",
        "address": "Jl. Ganesha No.10, Bandung 40132",
        "logo_file": "ITB.png",
        "id_format": generate_itb_nim,
        "colleges": ["STEI", "FTTM", "FTMD", "FTSL", "FMIPA", "SBM"]
    },
    10008581: { # UNAIR
        "name": "Universitas Airlangga",
        "domain": "unair.ac.id",
        "colors": ["#FFD700", "#000080"], # Kuning Biru
        "card_title": "KARTU TANDA MAHASISWA",
        "address": "Kampus C Mulyorejo, Surabaya 60115",
        "logo_file": "UNAIR.png",
        "id_format": generate_unair_nim,
        "colleges": ["Fakultas Kedokteran", "Fakultas Ekonomi dan Bisnis", "Fakultas Sains dan Teknologi"]
    },
    10008585: { # UB
        "name": "Universitas Brawijaya",
        "domain": "ub.ac.id",
        "colors": ["#003366", "#FFD700"],
        "card_title": "KARTU TANDA MAHASISWA",
        "address": "Jl. Veteran, Malang 65145",
        "logo_file": "UB.png",
        "id_format": generate_ub_nim,
        "colleges": ["Fakultas Teknik", "Fakultas Ilmu Komputer", "Fakultas Ekonomi dan Bisnis"]
    },
    10008587: { # UNDIP
        "name": "Universitas Diponegoro",
        "domain": "undip.ac.id",
        "colors": ["#000080", "#FFFFFF"],
        "card_title": "KARTU MAHASISWA",
        "address": "Jl. Prof. Sudarto, SH, Tembalang, Semarang 50275",
        "logo_file": "UNDIP.png",
        "id_format": lambda: generate_us_id(10), # Pola umum
        "colleges": ["Fakultas Teknik", "Fakultas Ekonomika dan Bisnis", "Fakultas Hukum"]
    },
    10008593: { # Telkom
        "name": "Telkom University",
        "domain": "telkomuniversity.ac.id",
        "colors": ["#BE0027", "#FFFFFF"], # Merah Telkom
        "card_title": "KTM / STUDENT ID",
        "address": "Jl. Telekomunikasi No. 1, Bandung 40257",
        "logo_file": "Telkom University.png",
        "id_format": lambda: f"110{random.randint(1000000, 9999999)}",
        "colleges": ["Fakultas Teknik Elektro", "Fakultas Informatika", "Fakultas Rekayasa Industri"]
    },
     10008591: { # BINUS
        "name": "BINUS University",
        "domain": "binus.ac.id",
        "colors": ["#F58220", "#000000"], # Oranye Binus
        "card_title": "BINUSIAN CARD",
        "address": "Jl. K. H. Syahdan No. 9, Jakarta 11480",
        "logo_file": "BINUS University.png",
        "id_format": lambda: f"2{random.randint(0,9)}{str(datetime.now().year)[2:]}{random.randint(10000, 99999)}",
        "colleges": ["School of Computer Science", "BINUS Business School", "School of Design"]
    },

    # ================= USA =================
    2565: { # Penn State
        "name": "The Pennsylvania State University",
        "domain": "psu.edu",
        "colors": ["#041E42", "#FFFFFF"],
        "card_title": "id+ Card",
        "address": "University Park, PA 16802",
        "logo_file": "Pennsylvania State University.png",
        "id_format": generate_penn_id,
        "colleges": ["University Park", "College of Engineering", "Smeal College of Business"]
    },
    3521: { # UF
        "name": "University of Florida",
        "domain": "ufl.edu",
        "colors": ["#FA4616", "#0021A5"], # Orange Blue
        "card_title": "Gator 1 Card",
        "address": "Gainesville, FL 32611",
        "logo_file": "University of Florida.png",
        "id_format": lambda: generate_us_id(8),
        "colleges": ["College of Engineering", "Warrington College of Business", "College of Liberal Arts and Sciences"]
    },
    10007832: { # Texas A&M
        "name": "Texas A&M University",
        "domain": "tamu.edu",
        "colors": ["#500000", "#FFFFFF"], # Maroon
        "card_title": "Aggie Card",
        "address": "College Station, TX 77843",
        "logo_file": "Texas A&M University.png",
        "id_format": lambda: generate_us_id(9),
        "colleges": ["College of Engineering", "Mays Business School"]
    },
    378: { # ASU
        "name": "Arizona State University",
        "domain": "asu.edu",
        "colors": ["#8C1D40", "#FFC627"], # Maroon Gold
        "card_title": "Sun Card",
        "address": "Tempe, AZ 85281",
        "logo_file": "Arizona State University.png",
        "id_format": lambda: generate_us_id(10),
        "colleges": ["Ira A. Fulton Schools of Engineering", "W. W. Carey School of Business"]
    },
     3568: { # U-Michigan
        "name": "University of Michigan",
        "domain": "umich.edu",
        "colors": ["#00274C", "#FFCB05"], # Maize & Blue
        "card_title": "MCard",
        "address": "Ann Arbor, MI 48109",
        "logo_file": "University of Michigan.png",
        "id_format": lambda: generate_us_id(8),
        "colleges": ["College of Engineering", "Ross School of Business", "LSA"]
    },
}

def get_university_preset(org_id):
    """Retrieve preset data for a given organization ID (int or str)"""
    try:
        oid = int(org_id)
        return UNIVERSITY_PRESETS.get(oid)
    except:
        return None
