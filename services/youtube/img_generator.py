"""Modul Pembuatan Kartu Mahasiswa PNG - Multi-University Support"""
import random
from datetime import datetime
from io import BytesIO
import base64
from . import config

def generate_psu_id():
    """Membuat PSU ID acak (9 digit angka)"""
    return f"9{random.randint(10000000, 99999999)}"

def generate_school_email(first_name, last_name, school=None):
    """
    Membuat email sekolah sesuai domain dengan pola dari referensi
    """
    if not school:
        school = config.SCHOOLS['2565'] # Default PSU
        
    domain = school.get('domain', 'edu')
    
    # Pola dari referensi
    patterns = [
        f"{first_name[0].lower()}{last_name.lower()}{random.randint(100, 999)}",
        f"{first_name.lower()}.{last_name.lower()}{random.randint(10, 99)}",
        f"{last_name.lower()}{first_name[0].lower()}{random.randint(100, 999)}"
    ]
    
    # Khusus domain tertentu (Opsional, pola di atas sudah umum)
    if 'psu.edu' in domain:
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 9999)}@psu.edu"
    else:
        email = f"{random.choice(patterns)}@{domain}"
        
    return email

def generate_psu_email(first_name, last_name):
    return generate_school_email(first_name, last_name, config.SCHOOLS['2565'])

def generate_html(first_name, last_name, email=None, school_id='2565'):
    """
    Membuat HTML Kartu Mahasiswa (Multi-School)
    """
    # 1. Setup Data
    school = config.SCHOOLS.get(school_id, config.SCHOOLS['2565'])
    name = f"{first_name} {last_name}"
    display_email = email if email else generate_school_email(first_name, last_name, school)
    
    now = datetime.now()
    date_str = now.strftime('%B %d, %Y')
    time_str = now.strftime('%I:%M:%S %p')
    
    if 1 <= now.month <= 5:
        current_term = f"Spring {now.year}"
    elif 6 <= now.month <= 8:
        current_term = f"Summer {now.year}"
    else:
        current_term = f"Fall {now.year}"

    majors = ['Computer Science', 'Business', 'Psychology', 'Engineering', 'Biology']
    major = random.choice(majors)
    
    # 2. Select Template
    
    # --- UCLA (3499) ---
    if school_id == '3499':
        ucla_id = f"{random.randint(100000000, 999999999)}"
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MyUCLA - Class Planner</title>
    <style>
        body {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; background: #f0f0f0; margin: 0; }}
        .header {{ background: #2774AE; color: white; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; border-bottom: 5px solid #FFD100; }}
        .logo {{ font-size: 24px; font-weight: bold; letter-spacing: 1px; }}
        .nav {{ background: #fff; padding: 10px 40px; border-bottom: 1px solid #ddd; font-size: 13px; color: #005587; font-weight: bold; }}
        .container {{ background: white; width: 1000px; margin: 30px auto; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); min-height: 700px; }}
        .page-title {{ color: #2774AE; border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }}
        .student-info {{ background: #f9f9f9; border: 1px solid #eee; padding: 15px; display: flex; justify-content: space-between; margin-bottom: 30px; }}
        .info-item {{ display: flex; flex-direction: column; }}
        .label {{ font-size: 11px; color: #666; text-transform: uppercase; }}
        .value {{ font-weight: bold; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #2774AE; color: white; padding: 10px; text-align: left; font-size: 12px; }}
        td {{ padding: 12px 10px; border-bottom: 1px solid #eee; font-size: 13px; }}
        .timestamp {{ text-align: right; color: #888; font-size: 11px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">MyUCLA</div>
        <div>{name} | Sign Out</div>
    </div>
    <div class="nav">Academics > Class Planner</div>
    <div class="container">
        <h1 class="page-title">Study List - {current_term}</h1>
        <div class="student-info">
            <div class="info-item"><span class="label">Name</span><span class="value">{name}</span></div>
            <div class="info-item"><span class="label">UID</span><span class="value">{ucla_id}</span></div>
            <div class="info-item"><span class="label">Email</span><span class="value">{display_email}</span></div>
            <div class="info-item"><span class="label">Major</span><span class="value">{major}</span></div>
            <div class="info-item"><span class="label">Status</span><span class="value" style="color:green">Enrolled</span></div>
        </div>
        <table>
            <thead><tr><th>Class</th><th>Course Title</th><th>Type</th><th>Days/Time</th><th>Units</th></tr></thead>
            <tbody>
                <tr><td>COM SCI 180</td><td>Algorithms</td><td>LEC</td><td>MW 2:00PM-3:50PM</td><td>4.0</td></tr>
                <tr><td>MATH 115A</td><td>Linear Algebra</td><td>LEC</td><td>TR 10:00AM-11:50AM</td><td>5.0</td></tr>
                <tr><td>PHYSICS 1A</td><td>Mechanics</td><td>LEC</td><td>MWF 9:00AM-9:50AM</td><td>5.0</td></tr>
                <tr><td>HIST 1C</td><td>Modern History</td><td>LEC</td><td>TR 2:00PM-3:15PM</td><td>4.0</td></tr>
            </tbody>
        </table>
        <div class="timestamp">Generated: {date_str} {time_str}</div>
    </div>
</body>
</html>"""

    # --- UMich (3568) ---
    elif school_id == '3568':
        umich_id = f"{random.randint(10000000, 99999999)}"
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wolverine Access - Backpack & Registration</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #fff; margin: 0; }}
        .header {{ background: #00274C; color: #FFCB05; padding: 20px; font-size: 20px; font-weight: bold; }}
        .subheader {{ background: #eee; padding: 10px 20px; border-bottom: 1px solid #ccc; font-size: 14px; font-weight: bold; color: #00274C; }}
        .container {{ padding: 30px 40px; width: 900px; margin: 0 auto; }}
        .card {{ border: 1px solid #ccc; padding: 20px; margin-bottom: 20px; }}
        .card-header {{ font-weight: bold; border-bottom: 2px solid #00274C; padding-bottom: 5px; margin-bottom: 15px; color: #00274C; }}
        .info-row {{ display: flex; margin-bottom: 10px; }}
        .info-key {{ width: 150px; color: #555; font-weight: bold; }}
        .info-val {{ flex: 1; }}
        table {{ width: 100%; border: 1px solid #ccc; border-collapse: collapse; margin-top: 15px; }}
        th {{ background: #f2f2f2; padding: 8px; border: 1px solid #ccc; font-size: 12px; }}
        td {{ padding: 8px; border: 1px solid #ccc; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">UNIVERSITY OF MICHIGAN</div>
    <div class="subheader">Wolverine Access > Student Business</div>
    <div class="container">
        <h2>View My Schedule</h2>
        <div class="card">
            <div class="card-header">{current_term} | Undergraduate | Ann Arbor</div>
            <div class="info-row"><div class="info-key">Name:</div><div class="info-val">{name}</div></div>
            <div class="info-row"><div class="info-key">ID:</div><div class="info-val">{umich_id}</div></div>
            <div class="info-row"><div class="info-key">Email:</div><div class="info-val">{display_email}</div></div>
            <div class="info-row"><div class="info-key">Program:</div><div class="info-val">{major}</div></div>
        </div>
        <table>
            <thead><tr><th>Class</th><th>Description</th><th>Days/Times</th><th>Room</th></tr></thead>
            <tbody>
                <tr><td>EECS 280</td><td>Prog & Data Struct</td><td>MoWe 1:30PM - 3:00PM</td><td>1013 DOW</td></tr>
                <tr><td>MATH 215</td><td>Calculus III</td><td>TuTh 8:30AM - 10:00AM</td><td>1200 CHEM</td></tr>
                <tr><td>STATS 250</td><td>Intro to Stats</td><td>MoWeFr 11:00AM - 12:00PM</td><td>AUD B AH</td></tr>
            </tbody>
        </table>
        <div style="margin-top:20px; font-size:11px; color:#666;">
            Run Date: {date_str}
        </div>
    </div>
</body>
</html>"""

    # --- PSU (Default) ---
    psu_id = f"9{random.randint(10000000, 99999999)}"
    term_dates = "Jan - May" if "Spring" in current_term else ("May - Aug" if "Summer" in current_term else "Aug - Dec")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LionPATH - Student Home</title>
    <style>
        :root {{ --psu-blue: #1E407C; --text-color: #333; }}
        body {{ font-family: "Roboto", Helvetica, Arial, sans-serif; background-color: #e0e0e0; margin: 0; padding: 20px; color: var(--text-color); display: flex; justify-content: center; }}
        .viewport {{ width: 100%; max-width: 1100px; background-color: #fff; box-shadow: 0 5px 20px rgba(0,0,0,0.15); min-height: 800px; display: flex; flex-direction: column; }}
        .header {{ background-color: var(--psu-blue); color: white; padding: 15px 25px; display: flex; align-items: center; justify-content: space-between; }}
        .psu-logo-text {{ font-family: "Georgia", serif; font-size: 24px; font-weight: bold; }}
        .system-name {{ font-size: 20px; font-weight: 300; border-left: 1px solid rgba(255,255,255,0.4); padding-left: 15px; margin-left: 15px; }}
        .nav-bar {{ background-color: #f8f8f8; border-bottom: 1px solid #ddd; padding: 12px 25px; font-size: 14px; color: #555; display: flex; gap: 30px; }}
        .nav-item.active {{ color: var(--psu-blue); font-weight: bold; border-bottom: 3px solid var(--psu-blue); padding-bottom: 5px; }}
        .content {{ padding: 40px; flex: 1; }}
        .page-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 2px solid #eee; padding-bottom: 15px; }}
        .page-title {{ font-size: 28px; color: var(--psu-blue); margin: 0; font-weight: 400; }}
        .student-card {{ background: #fff; border: 1px solid #ddd; border-top: 4px solid var(--psu-blue); padding: 20px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
        .info-group {{ display: flex; flex-direction: column; }}
        .info-label {{ color: #666; font-size: 12px; text-transform: uppercase; margin-bottom: 6px; font-weight: 600; }}
        .info-val {{ font-weight: bold; color: #222; font-size: 15px; }}
        .status-badge {{ display: inline-block; background-color: #e6fffa; color: #007a5e; padding: 6px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #b2f5ea; font-size: 13px; }}
        .data-timestamp {{ margin-bottom: 15px; font-size: 13px; color: #555; text-align: right; background: #f9f9f9; display: inline-block; padding: 5px 10px; border-radius: 4px; border: 1px solid #eee; float: right; }}
        .schedule-table {{ width: 100%; border-collapse: collapse; font-size: 14px; clear: both; }}
        .schedule-table th {{ text-align: left; padding: 12px; background-color: #f4f6f9; border-bottom: 2px solid #ccc; font-size: 11px; text-transform: uppercase; }}
        .schedule-table td {{ padding: 15px 12px; border-bottom: 1px solid #eee; }}
        .course-code {{ font-weight: bold; color: var(--psu-blue); }}
    </style>
</head>
<body>
<div class="viewport">
    <div class="header">
        <div class="header-left" style="display:flex;align-items:center">
            <div style="display:flex;flex-direction:column">
                <div class="psu-logo-text">PennState</div>
                <div style="font-size:11px;text-transform:uppercase;opacity:0.9">The Pennsylvania State University</div>
            </div>
            <div class="system-name">LionPATH</div>
        </div>
        <div>Welcome, <strong>{name}</strong></div>
    </div>
    <div class="nav-bar">
        <div class="nav-item">Student Home</div>
        <div class="nav-item active">My Class Schedule</div>
        <div class="nav-item">Academics</div>
        <div class="nav-item">Finances</div>
    </div>
    <div class="content">
        <div class="page-header">
            <h1 class="page-title">My Class Schedule</h1>
            <div style="background:#fff;border:1px solid #ccc;padding:8px 15px;border-radius:4px">Term: <strong>{current_term}</strong></div>
        </div>
        <div class="student-card">
            <div class="info-group"><div class="info-label">Student Name</div><div class="info-val">{name}</div></div>
            <div class="info-group"><div class="info-label">Student ID / Email</div><div class="info-val">{psu_id} / {display_email}</div></div>
            <div class="info-group"><div class="info-label">Enrollment Status</div><div class="status-badge">✅ Full-Time Student</div></div>
            <div class="info-group"><div class="info-label">Academic Program</div><div class="info-val">{major} (BS)</div></div>
            <div class="info-group"><div class="info-label">Campus</div><div class="info-val">University Park (Main)</div></div>
            <div class="info-group"><div class="info-label">Semester Dates</div><div class="info-val">{term_dates}, {now.year}</div></div>
        </div>
        <div class="data-timestamp">Generated on: <strong>{date_str}</strong> at {time_str}</div>
        <table class="schedule-table">
            <thead><tr><th>Course</th><th>Title</th><th>Days & Times</th><th>Location</th><th>Credits</th></tr></thead>
            <tbody>
                <tr><td class="course-code">CMPSC 465</td><td>Data Structures</td><td>MoWeFr 10:10AM - 11:00AM</td><td>Willard 062</td><td>3.00</td></tr>
                <tr><td class="course-code">MATH 230</td><td>Calculus</td><td>TuTh 1:35PM - 2:50PM</td><td>Thomas 102</td><td>4.00</td></tr>
                <tr><td class="course-code">ENGL 202C</td><td>Tech Writing</td><td>Fr 1:25PM - 2:15PM</td><td>Boucke 304</td><td>3.00</td></tr>
            </tbody>
        </table>
    </div>
</div>
</body>
</html>"""
    return html


async def generate_image(first_name, last_name, email=None, school_id='2565'):
    """
    Membuat screenshot PNG Penn State LionPATH (Async)

    Args:
        first_name: Nama depan
        last_name: Nama belakang
        school_id: ID sekolah

    Returns:
        bytes: Data gambar PNG
    """
    try:
        from playwright.async_api import async_playwright

        # Buat HTML
        html_content = generate_html(first_name, last_name, email, school_id)

        # Gunakan Playwright untuk screenshot (Async)
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = await browser.new_page(viewport={'width': 1200, 'height': 900})
            await page.set_content(html_content, wait_until='load')
            await page.wait_for_timeout(500)  # Tunggu style loading
            screenshot_bytes = await page.screenshot(type='png', full_page=True)
            await browser.close()

        return screenshot_bytes

    except ImportError:
        raise Exception("Perlu install playwright: pip install playwright && playwright install chromium")
    except Exception as e:
        raise Exception(f"Gagal membuat gambar: {str(e)}")


if __name__ == '__main__':
    # Test code
    import sys
    import io

    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("Test Multi-School Image Gen...")
    
    first_name = "Test"
    last_name = "User"
    
    # Test all 3 schools
    schools = ['2565', '3499', '3568']
    
    import asyncio
    
    async def run_tests():
        for sid in schools:
            print(f"Testing School ID: {sid}")
            try:
                img = await generate_image(first_name, last_name, None, sid)
                print(f"✅ Success. Size: {len(img)}")
            except Exception as e:
                print(f"❌ Failed: {e}")

    asyncio.run(run_tests())
