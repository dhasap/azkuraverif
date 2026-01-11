"""
Modul untuk menghasilkan data fiktif untuk dokumen verifikasi
Mengadaptasi fungsi-fungsi dari @faker-js/faker di azkuraidgen/src/utils/dataGenerator.js
"""
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_random_data():
    """
    Menghasilkan data fiktif untuk berbagai jenis dokumen verifikasi
    Berdasarkan fungsi generateRandomData() dari dataGenerator.js
    """
    # Generate a past date for statement
    statement_date = fake.date_between(start_date='-6m', end_date='today')
    # Due date is typically 2-4 weeks after statement
    due_date = statement_date + timedelta(days=random.randint(14, 30))

    # Issue date typically current or very recent
    issue_date = fake.date_between(start_date='-5d', end_date='today')

    # Format dates
    statement_date_str = statement_date.strftime('%m/%d/%Y')
    due_date_str = due_date.strftime('%m/%d/%Y')
    issue_date_str = issue_date.strftime('%m/%d/%Y')

    # Generate names
    first_name = fake.first_name()
    last_name = fake.last_name()

    # Common Texas/US universities to choose from if desired, or just generic
    university = "Hachimi University"

    # Course Data Pool based on Major
    majors = [
        {"name": "Computer Science", "college": "College of Science and Engineering", "program": "Bachelor of Science", "prefix": "CS"},
        {"name": "Business Administration", "college": "McCoy College of Business", "program": "Bachelor of Business Admin", "prefix": "BA"},
        {"name": "Psychology", "college": "College of Liberal Arts", "program": "Bachelor of Arts", "prefix": "PSY"},
        {"name": "Biology", "college": "College of Science and Engineering", "program": "Bachelor of Science", "prefix": "BIO"},
        {"name": "Marketing", "college": "McCoy College of Business", "program": "Bachelor of Business Admin", "prefix": "MKT"},
    ]

    selected_major = random.choice(majors)

    # Generate random courses logic
    def generate_courses(major_prefix, term):
        common_courses = [
            {"code": "ENG 1310", "name": "College Writing I", "hours": 3},
            {"code": "ENG 1320", "name": "College Writing II", "hours": 3},
            {"code": "HIST 1310", "name": "History of US to 1877", "hours": 3},
            {"code": "POSI 2310", "name": "Principles of American Govt", "hours": 3},
            {"code": "COMM 1310", "name": "Fund. of Human Communication", "hours": 3},
            {"code": "PHIL 1305", "name": "Philosophy & Critical Thinking", "hours": 3},
            {"code": "ART 2313", "name": "Introduction to Fine Arts", "hours": 3},
        ]

        major_courses_pool = {
            "CS": [
                {"code": "CS 1428", "name": "Foundations of Computer Science I", "hours": 4},
                {"code": "CS 2308", "name": "Foundations of Computer Science II", "hours": 3},
                {"code": "CS 3358", "name": "Data Structures", "hours": 3},
                {"code": "MATH 2471", "name": "Calculus I", "hours": 4},
                {"code": "MATH 2358", "name": "Discrete Mathematics I", "hours": 3},
            ],
            "BA": [
                {"code": "MGT 3303", "name": "Management of Organizations", "hours": 3},
                {"code": "MKT 3343", "name": "Principles of Marketing", "hours": 3},
                {"code": "ACC 2361", "name": "Intro to Financial Accounting", "hours": 3},
                {"code": "ECO 2314", "name": "Principles of Microeconomics", "hours": 3},
                {"code": "FIN 3312", "name": "Business Finance", "hours": 3},
            ],
            "PSY": [
                {"code": "PSY 1300", "name": "Introduction to Psychology", "hours": 3},
                {"code": "PSY 3300", "name": "Lifespan Development", "hours": 3},
                {"code": "PSY 3322", "name": "Brain and Behavior", "hours": 3},
                {"code": "SOC 1310", "name": "Introduction to Sociology", "hours": 3},
                {"code": "PSY 3341", "name": "Cognitive Processes", "hours": 3},
            ],
            "BIO": [
                {"code": "BIO 1330", "name": "Functional Biology", "hours": 3},
                {"code": "BIO 1130", "name": "Functional Biology Lab", "hours": 1},
                {"code": "CHEM 1341", "name": "General Chemistry I", "hours": 3},
                {"code": "CHEM 1141", "name": "General Chemistry I Lab", "hours": 1},
                {"code": "BIO 2450", "name": "Genetics", "hours": 4},
            ],
            "MKT": [
                {"code": "MKT 3350", "name": "Consumer Behavior", "hours": 3},
                {"code": "MKT 3358", "name": "Professional Selling", "hours": 3},
                {"code": "MKT 4330", "name": "Promotional Strategy", "hours": 3},
                {"code": "BLAW 2361", "name": "Legal Environment of Business", "hours": 3},
                {"code": "QMST 2333", "name": "Business Statistics", "hours": 3},
            ]
        }

        # Mix 2-3 major courses with 2-3 common courses for realism
        num_major = random.randint(2, 3)
        num_common = 5 - num_major

        my_major_courses = random.sample(major_courses_pool[major_prefix], num_major)
        my_common_courses = random.sample(common_courses, num_common)

        combined = my_major_courses + my_common_courses

        # Generate Grades and Quality Points
        result = []
        for c in combined:
            grade_pool = ['A', 'A', 'A', 'A', 'B', 'B']  # Heavily skew towards A and B to ensure passing and realistic "good student" GPA
            grade = random.choice(grade_pool)
            
            points_per_hour = 0
            if grade == 'A': 
                points_per_hour = 4
            elif grade == 'B': 
                points_per_hour = 3
            elif grade == 'C': 
                points_per_hour = 2
            elif grade == 'D': 
                points_per_hour = 1

            result.append({
                **c,
                "grade": grade,
                "quality_points": round(c["hours"] * points_per_hour, 2),
                "hours": round(float(c["hours"]), 2)
            })
        
        return result

    term_courses = generate_courses(selected_major["prefix"], "Fall 2024")
    spring_courses = generate_courses(selected_major["prefix"], "Spring 2025")

    # Calculate GPA logic
    def calculate_term_stats(courses):
        attempted = sum(float(c["hours"]) for c in courses)
        earned = attempted  # Assuming no Fs
        quality_points = sum(float(c["quality_points"]) for c in courses)
        gpa = round(quality_points / attempted, 2) if attempted > 0 else 0
        return {"attempted": attempted, "earned": earned, "quality_points": quality_points, "gpa": gpa}

    fall_stats = calculate_term_stats(term_courses)
    spring_stats = calculate_term_stats(spring_courses)

    # Cumulative (mock previous data + current)
    prev_hours = random.randint(15, 60)
    prev_gpa = round(random.uniform(3.2, 4.0), 2)  # Ensure previous GPA is solid (above 3.2)
    prev_points = prev_hours * prev_gpa

    cum_attempted = prev_hours + fall_stats["attempted"] + spring_stats["attempted"]
    cum_points = prev_points + fall_stats["quality_points"] + spring_stats["quality_points"]
    cum_gpa = round(cum_points / cum_attempted, 2)

    # Tuition Data Logic
    # Base tuition around 9500, slightly random but rounded to whole number
    base_tuition = random.randint(9400, 9800)

    # Differential tuition depends on college (mock logic)
    if "Business" in selected_major["college"]:
        diff_tuition = 1100
    elif "Science" in selected_major["college"]:
        diff_tuition = 975
    else:
        diff_tuition = 850

    fees = {
        "student_service": 340,
        "computer_service": 210,
        "library": 150,
        "medical": 95,
        "other": 680,
        "intl_ops": 75,
        "insurance": 1650
    }

    total_fees = sum(fees.values()) + diff_tuition
    total_charges = base_tuition + total_fees

    # Admission date: 1-3 years ago (ensures student card remains valid)
    years_enrolled = random.randint(1, 3)
    admission_date = datetime.now() - timedelta(days=years_enrolled*365)
    # Randomize to a semester start (Aug/Sep or Jan/Feb)
    admission_month = random.choice([0, 1, 7, 8])  # Jan, Feb, Aug, Sep
    admission_day = random.randint(15, 28)
    admission_date = admission_date.replace(month=admission_month+1, day=admission_day)
    admission_date_str = admission_date.strftime('%m/%d/%Y')

    # Student Card issued 1-4 weeks after admission
    card_issue_date = admission_date + timedelta(days=random.randint(7, 28))
    card_issue_date_str = card_issue_date.strftime('%m/%d/%Y')

    # Valid for 4 years from issue
    card_valid_date = card_issue_date + timedelta(days=4*365)
    card_valid_date_str = card_valid_date.strftime('%m/%d/%Y')

    return {
        "university_name": university,
        "university_logo": "/university-logo.png",
        "university_address": f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()}, {fake.zipcode()}",
        "student_name": f"{last_name} {first_name}",
        "student_id": f"{random.randint(100000, 999999)}-{random.randint(1000, 9999)}",
        "passport_number": fake.passport_number().upper(),  # Added passport
        "address": f"{fake.street_address()}, {fake.city()}, {fake.state()}",
        "term": "Fall 2024",
        "major": selected_major["name"],
        "program": selected_major["program"],
        "college": selected_major["college"],
        "statement_date": statement_date_str,
        "due_date": due_date_str,
        "issue_date": issue_date_str,
        "admission_date": admission_date_str,  # Added admission date
        "officials": {
            "dean": f"{fake.last_name()}, {fake.first_name()} (PhD)",
            "registrar": f"{fake.last_name()}, {fake.first_name()}"
        },
        "tuition": {
            "base": f"${base_tuition:,}",
            "differential": f"${diff_tuition:,}",
            "fees": fees,
            "total": f"${total_charges:,}"
        },
        "courses": {
            "current": term_courses,
            "next": spring_courses
        },
        "stats": {
            "current": fall_stats,
            "next": spring_stats,
            "cumulative": {
                "attempted": round(cum_attempted, 2),
                "earned": round(cum_attempted, 2),
                "quality_points": round(cum_points, 2),
                "gpa": cum_gpa
            }
        },
        # Student Card specific
        "card_subtitle": 'INTERNATIONAL STUDENT ID CARD',
        "card_issue_date": card_issue_date_str,
        "card_valid_date": card_valid_date_str,
        "card_notice": 'This card is the property of the university and must be returned upon request. If found, please return to the nearest university office.',
        "card_color": random.choice(['#3b82f6', '#10b981', '#8b5cf6', '#ef4444', '#f59e0b', '#06b6d4', '#ec4899']),
        "student_photo": None
    }


def generate_teacher_data():
    """
    Menghasilkan data fiktif untuk dokumen verifikasi guru
    Berdasarkan fungsi generateTeacherData() dari dataGenerator.js
    """
    def format_date(date):
        return date.strftime('%m/%d/%Y')

    first_name = fake.first_name()
    last_name = fake.last_name()
    title = random.choice(['Dr.', 'Prof.', 'Mr.', 'Ms.', 'Mrs.'])

    # University/Institution
    universities = [
        {"name": "California State University", "city": "Los Angeles", "state": "CA", "abbr": "CSU"},
        {"name": "University of Texas", "city": "Austin", "state": "TX", "abbr": "UT"},
        {"name": "Florida International University", "city": "Miami", "state": "FL", "abbr": "FIU"},
        {"name": "Arizona State University", "city": "Tempe", "state": "AZ", "abbr": "ASU"},
        {"name": "George Mason University", "city": "Fairfax", "state": "VA", "abbr": "GMU"}
    ]
    selected_university = random.choice(universities)

    # Department and subjects
    departments = [
        {
            "name": "Computer Science",
            "college": "College of Engineering and Computer Science",
            "subjects": ["Data Structures and Algorithms", "Software Engineering", "Database Management Systems", "Computer Networks"],
            "positions": ["Assistant Professor", "Associate Professor", "Professor", "Lecturer"]
        },
        {
            "name": "Mathematics",
            "college": "College of Natural Sciences and Mathematics",
            "subjects": ["Calculus I & II", "Linear Algebra", "Statistical Methods", "Discrete Mathematics"],
            "positions": ["Assistant Professor", "Associate Professor", "Professor"]
        },
        {
            "name": "Business Administration",
            "college": "School of Business",
            "subjects": ["Principles of Management", "Marketing Strategy", "Corporate Finance", "Macroeconomics"],
            "positions": ["Assistant Professor", "Associate Professor", "Professor", "Clinical Professor"]
        },
        {
            "name": "Psychology",
            "college": "College of Liberal Arts and Social Sciences",
            "subjects": ["Introduction to Psychology", "Research Methods", "Cognitive Psychology", "Abnormal Psychology"],
            "positions": ["Assistant Professor", "Associate Professor", "Professor"]
        },
        {
            "name": "English",
            "college": "College of Liberal Arts and Social Sciences",
            "subjects": ["Composition and Rhetoric", "American Literature", "Creative Writing", "Literary Analysis"],
            "positions": ["Assistant Professor", "Associate Professor", "Professor", "Lecturer"]
        }
    ]

    selected_department = random.choice(departments)

    # Employment details
    hire_date = fake.date_between(start_date='-12y', end_date='-1y')
    employee_id = f"{selected_university['abbr']}-{random.randint(100000, 999999)}"

    # Teacher ID Card dates
    id_issue_date = hire_date + timedelta(days=random.randint(30, 90))
    id_valid_date = id_issue_date + timedelta(days=4*365)

    # Teaching certificate
    certification_date = hire_date - timedelta(days=random.randint(180, 730))

    # Salary details (more realistic ranges by position)
    position = random.choice(selected_department["positions"])
    
    if position == "Lecturer":
        base_salary = random.randint(45000, 65000)
    elif position == "Assistant Professor":
        base_salary = random.randint(65000, 85000)
    elif position == "Associate Professor":
        base_salary = random.randint(80000, 110000)
    elif position == "Professor":
        base_salary = random.randint(100000, 140000)
    elif position == "Clinical Professor":
        base_salary = random.randint(90000, 120000)
    else:
        base_salary = random.randint(65000, 95000)

    pay_period_start = fake.date_between(start_date='-30d', end_date='today')
    pay_period_end = pay_period_start + timedelta(days=14)

    # Office and contact details
    building = random.choice(['Science Building', 'Engineering Hall', 'Liberal Arts Center', 'Business Complex', 'Academic Center'])
    office_number = f"{random.randint(1, 5)}{random.randint(100, 999)}"
    phone_ext = f"{random.randint(1000, 9999)}"

    return {
        # Basic Info
        "university_name": selected_university["name"],
        "university_city": selected_university["city"],
        "university_state": selected_university["state"],
        "university_abbr": selected_university["abbr"],
        "university_logo": "/university-logo.png",
        "university_address": f"{fake.street_address()}, {selected_university['city']}, {selected_university['state']} {fake.zipcode()}",
        "teacher_title": title,
        "teacher_name": f"{last_name}, {first_name}",
        "teacher_first_name": first_name,
        "teacher_last_name": last_name,
        "teacher_full_name": f"{title} {first_name} {last_name}",
        "employee_id": employee_id,
        "address": f"{fake.street_address()}, {selected_university['state']} {fake.zipcode()}",

        # Office Info
        "office": f"{building}, Room {office_number}",
        "phone": f"({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)} ext. {phone_ext}",
        "email": f"{first_name.lower()}.{last_name.lower()}@{selected_university['name'].lower().replace(' ', '')}.edu",

        # Academic Info
        "department": selected_department["name"],
        "college": selected_department["college"],
        "position": position,
        "subjects": selected_department["subjects"],

        # Dates
        "hire_date": format_date(hire_date),
        "certification_date": format_date(certification_date),
        "pay_period_start": format_date(pay_period_start),
        "pay_period_end": format_date(pay_period_end),

        # Teacher ID Card
        "id_issue_date": format_date(id_issue_date),
        "id_valid_date": format_date(id_valid_date),
        "id_card_subtitle": 'FACULTY IDENTIFICATION CARD',
        "id_color": random.choice(['#dc2626', '#059669', '#7c3aed', '#d97706', '#0891b2']),

        # Salary info
        "base_salary": base_salary,
        "salary_formatted": f"${base_salary:,}",

        # Officials
        "officials": {
            "dean": f"Dr. {fake.first_name()} {fake.last_name()}",
            "hr": f"{fake.first_name()} {fake.last_name()}",
            "principal": f"Dr. {fake.first_name()} {fake.last_name()}",
            "provost": f"Dr. {fake.first_name()} {fake.last_name()}"
        },

        "teacher_photo": None
    }


def generate_admission_letter_data():
    """
    Menghasilkan data untuk surat penerimaan
    """
    data = generate_random_data()
    admission_date = fake.date_between(start_date='-1y', end_date='today')
    
    return {
        **data,
        "letter_date": fake.date_between(start_date='-3m', end_date='today').strftime('%m/%d/%Y'),
        "admission_date": admission_date.strftime('%m/%d/%Y'),
        "program_admitted": data["major"],
        "academic_year": f"{admission_date.year}-{admission_date.year+1}",
        "letter_content": f"""
Dear {data["student_name"]},

We are pleased to inform you that you have been admitted to {data["university_name"]} for the {data["major"]} program in the {data["academic_year"]} academic year. Your enrollment is conditional upon meeting all academic and administrative requirements.

Please confirm your acceptance by the deadline and contact the admissions office if you have any questions.

Sincerely,
{data["officials"]["dean"]}
Dean of Admissions
{data["university_name"]}
        """.strip()
    }


def generate_enrollment_certificate_data():
    """
    Menghasilkan data untuk sertifikat pendaftaran
    """
    data = generate_random_data()
    
    return {
        **data,
        "certificate_date": fake.date_between(start_date='-1m', end_date='today').strftime('%m/%d/%Y'),
        "enrollment_status": "Full-time",
        "academic_level": "Undergraduate",
        "registration_number": f"REG-{random.randint(100000, 999999)}",
        "certificate_content": f"""
This is to certify that {data["student_name"]}, ID {data["student_id"]}, is officially enrolled as a {data["academic_level"]} student in the {data["major"]} program at {data["university_name"]} for the current academic year.

Issued on: {data["certificate_date"]}
Registration Number: {data["registration_number"]}
        """.strip()
    }


def generate_schedule_data():
    """
    Menghasilkan data untuk jadwal kuliah
    """
    data = generate_random_data()
    
    # Generate sample schedule
    schedule = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    times = ["08:00-09:15 AM", "09:30-10:45 AM", "11:00-12:15 PM", "01:00-02:15 PM", "02:30-03:45 PM", "04:00-05:15 PM"]
    
    for day in days[:4]:  # Only 4 days for sample
        num_classes = random.randint(2, 4)
        selected_times = random.sample(times, num_classes)
        for time in selected_times:
            course = random.choice(data["courses"]["current"])
            schedule.append({
                "day": day,
                "time": time,
                "course_code": course["code"],
                "course_name": course["name"],
                "location": f"{random.choice(['Main', 'Science', 'Arts'])} Building {random.randint(100, 499)}"
            })
    
    return {
        **data,
        "semester": "Fall 2024",
        "schedule": schedule
    }


def generate_employment_letter_data():
    """
    Menghasilkan data untuk surat kerja guru
    """
    data = generate_teacher_data()
    
    return {
        **data,
        "letter_date": fake.date_between(start_date='-1m', end_date='today').strftime('%m/%d/%Y'),
        "employment_status": "Full-time",
        "employment_terms": f"This letter confirms employment as {data['position']} in the {data['department']} department.",
        "letter_content": f"""
Dear {data["teacher_full_name"]},

This letter confirms your employment with {data["university_name"]} as a {data["position"]} in the {data["department"]} department, effective {data["hire_date"]}. Your employment is subject to the terms and conditions outlined in the faculty handbook.

Sincerely,
{data["officials"]["dean"]}
Dean of Faculty Affairs
{data["university_name"]}
        """.strip()
    }


def generate_salary_statement_data():
    """
    Menghasilkan data untuk pernyataan gaji guru
    """
    data = generate_teacher_data()
    
    deductions = {
        "tax": round(data["base_salary"] * 0.15, 2),
        "social_security": round(data["base_salary"] * 0.062, 2),
        "medicare": round(data["base_salary"] * 0.0145, 2),
        "health_insurance": 250.00,
        "retirement": round(data["base_salary"] * 0.05, 2)
    }
    
    gross_pay = data["base_salary"] / 24  # Assuming 24 pay periods per year
    total_deductions = sum(deductions.values())
    net_pay = gross_pay - total_deductions
    
    return {
        **data,
        "period_ending": data["pay_period_end"],
        "gross_pay": f"${gross_pay:,.2f}",
        "net_pay": f"${net_pay:,.2f}",
        "deductions": deductions,
        "payment_method": "Direct Deposit",
        "account_info": f"Account ending in ****{random.randint(1000, 9999)}"
    }


def generate_teaching_certificate_data():
    """
    Menghasilkan data untuk sertifikat mengajar guru
    """
    data = generate_teacher_data()
    
    return {
        **data,
        "certificate_date": data["certification_date"],
        "certificate_number": f"TC-{random.randint(100000, 999999)}",
        "valid_from": data["hire_date"],
        "valid_until": (datetime.strptime(data["hire_date"], '%m/%d/%Y') + timedelta(days=365*5)).strftime('%m/%d/%Y'),
        "certificate_content": f"""
This is to certify that {data["teacher_full_name"]}, Employee ID {data["employee_id"]}, holds a valid teaching certificate for the {data["department"]} department at {data["university_name"]}.
        
Certificate Number: {data["certificate_number"]}
Valid From: {data["valid_from"]}
Valid Until: {data["valid_until"]}
        """.strip()
    }