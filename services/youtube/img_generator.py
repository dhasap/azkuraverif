"""Modul Pembuatan Kartu Mahasiswa PNG - Penn State LionPATH"""
import random
from datetime import datetime
from io import BytesIO
import base64


def generate_psu_id():
    """Membuat PSU ID acak (9 digit angka)"""
    return f"9{random.randint(10000000, 99999999)}"


def generate_psu_email(first_name, last_name):
    """
    Membuat email PSU
    Format: firstName.lastName + 3-4 digit angka @psu.edu
    """
    digit_count = random.choice([3, 4])
    digits = ''.join([str(random.randint(0, 9)) for _ in range(digit_count)])
    email = f"{first_name.lower()}.{last_name.lower()}{digits}@psu.edu"
    return email


def generate_html(first_name, last_name, email=None, school_id='2565'):


    """


    Membuat Penn State LionPATH HTML


    """


    psu_id = generate_psu_id()


    name = f"{first_name} {last_name}"


    


    # Gunakan email yang diberikan atau email default PSU


    display_email = email if email else generate_psu_email(first_name, last_name)


    


    # Waktu dinamis


    now = datetime.now()


    date_str = now.strftime('%B %d, %Y')


    time_str = now.strftime('%I:%M:%S %p')


    


    # Logika Semester Otomatis


    if 1 <= now.month <= 5:


        current_term = f"Spring {now.year}"


        term_dates = "Jan 12 - May 08"


    elif 6 <= now.month <= 7:


        current_term = f"Summer {now.year}"


        term_dates = "May 15 - Aug 10"


    else:


        current_term = f"Fall {now.year}"


        term_dates = "Aug 25 - Dec 18"





    # Pilih jurusan


    majors = ['Computer Science (BS)', 'Software Engineering (BS)', 'Data Science (BS)', 'Information Systems (BS)']


    major = random.choice(majors)





    html = f"""<!DOCTYPE html>


<html lang="en">


<head>


    <meta charset="UTF-8">


    <meta name="viewport" content="width=device-width, initial-scale=1.0">


    <title>LionPATH - Student Home</title>


    <style>


        :root {{


            --psu-blue: #1E407C;


            --psu-light-blue: #96BEE6;


            --bg-gray: #f4f4f4;


            --text-color: #333;


        }}





        body {{


            font-family: "Roboto", "Helvetica Neue", Helvetica, Arial, sans-serif;


            background-color: #e0e0e0;


            margin: 0;


            padding: 20px;


            color: var(--text-color);


            display: flex;


            justify-content: center;


        }}





        .viewport {{


            width: 100%;


            max-width: 1100px;


            background-color: #fff;


            box-shadow: 0 5px 20px rgba(0,0,0,0.15);


            min-height: 800px;


            display: flex;


            flex-direction: column;


        }}





        .header {{


            background-color: var(--psu-blue);


            color: white;


            padding: 15px 25px;


            display: flex;


            align-items: center;


            justify-content: space-between;


        }}





        .brand-container {{ display: flex; flex-direction: column; }}


        .psu-logo-text {{ font-family: "Georgia", serif; font-size: 24px; font-weight: bold; }}


        .psu-sub-text {{ font-size: 11px; text-transform: uppercase; opacity: 0.9; }}


        .system-name {{ font-size: 20px; font-weight: 300; border-left: 1px solid rgba(255,255,255,0.4); padding-left: 15px; margin-left: 15px; }}





        .nav-bar {{ background-color: #f8f8f8; border-bottom: 1px solid #ddd; padding: 12px 25px; font-size: 14px; color: #555; display: flex; gap: 30px; }}


        .nav-item.active {{ color: var(--psu-blue); font-weight: bold; border-bottom: 3px solid var(--psu-blue); padding-bottom: 5px; }}





        .content {{ padding: 40px; flex: 1; }}


        .page-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 2px solid #eee; padding-bottom: 15px; }}


        .page-title {{ font-size: 28px; color: var(--psu-blue); margin: 0; font-weight: 400; }}


        .term-selector {{ background: #fff; border: 1px solid #ccc; padding: 8px 15px; border-radius: 4px; font-size: 15px; }}





        .student-card {{


            background: #fff;


            border: 1px solid #ddd;


            border-top: 4px solid var(--psu-blue);


            padding: 20px;


            margin-bottom: 30px;


            display: grid;


            grid-template-columns: repeat(3, 1fr);


            gap: 20px;


        }}


        .info-group {{ display: flex; flex-direction: column; }}


        .info-label {{ color: #666; font-size: 12px; text-transform: uppercase; margin-bottom: 6px; font-weight: 600; }}


        .info-val {{ font-weight: bold; color: #222; font-size: 15px; }}


        


        .status-badge {{


            display: inline-block;


            background-color: #e6fffa; color: #007a5e;


            padding: 6px 12px; border-radius: 20px; 


            font-weight: bold; border: 1px solid #b2f5ea;


            font-size: 13px;


        }}





        .data-timestamp {{


            margin-bottom: 15px; font-size: 13px; color: #555; text-align: right;


            background: #f9f9f9; display: inline-block; padding: 5px 10px; border-radius: 4px; border: 1px solid #eee; float: right;


        }}





        .schedule-table {{ width: 100%; border-collapse: collapse; font-size: 14px; clear: both; }}


        .schedule-table th {{ text-align: left; padding: 12px; background-color: #f4f6f9; border-bottom: 2px solid #ccc; font-size: 11px; text-transform: uppercase; }}


        .schedule-table td {{ padding: 15px 12px; border-bottom: 1px solid #eee; }}


        .course-code {{ font-weight: bold; color: var(--psu-blue); }}


    </style>


</head>


<body>





<div class="viewport">


    <div class="header">


        <div class="header-left">


            <div class="brand-container">


                <div class="psu-logo-text">PennState</div>


                <div class="psu-sub-text">The Pennsylvania State University</div>


            </div>


            <div class="system-name">LionPATH</div>


        </div>


        <div class="user-menu"><span>Welcome, <strong>{name}</strong></span></div>


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


            <div class="term-selector">Term: <strong>{current_term}</strong></div>


        </div>





        <div class="student-card">


            <div class="info-group">


                <div class="info-label">Student Name</div>


                <div class="info-val">{name}</div>


            </div>


            <div class="info-group">


                <div class="info-label">Student ID / Email</div>


                <div class="info-val">{psu_id} / {display_email}</div>


            </div>


            <div class="info-group">


                <div class="info-label">Enrollment Status</div>


                <div class="status-badge">✅ Full-Time Student</div>


            </div>


            <div class="info-group">


                <div class="info-label">Academic Program</div>


                <div class="info-val">{major}</div>


            </div>


            <div class="info-group">


                <div class="info-label">Campus</div>


                <div class="info-val">University Park (Main)</div>


            </div>


            <div class="info-group">


                <div class="info-label">Semester Dates</div>


                <div class="info-val">{term_dates}, {now.year}</div>


            </div>


        </div>





        <div class="data-timestamp">Generated on: <strong>{date_str}</strong> at {time_str}</div>





        <table class="schedule-table">


            <thead>


                <tr>


                    <th>Course</th>


                    <th>Title</th>


                    <th>Days & Times</th>


                    <th>Location</th>


                    <th>Credits</th>


                </tr>


            </thead>


            <tbody>


                <tr>


                    <td class="course-code">CMPSC 465</td>


                    <td>Data Structures and Algorithms</td>


                    <td>MoWeFr 10:10AM - 11:00AM</td>


                    <td>Willard 062</td>


                    <td>3.00</td>


                </tr>


                <tr>


                    <td class="course-code">MATH 230</td>


                    <td>Calculus and Vector Analysis</td>


                    <td>TuTh 1:35PM - 2:50PM</td>


                    <td>Thomas 102</td>


                    <td>4.00</td>


                </tr>


                <tr>


                    <td class="course-code">ENGL 202C</td>


                    <td>Technical Writing</td>


                    <td>Fr 1:25PM - 2:15PM</td>


                    <td>Boucke 304</td>


                    <td>3.00</td>


                </tr>


            </tbody>


        </table>


    </div>


</div>





</body>


</html>


"""


    return html




    return html


async def generate_image(first_name, last_name, email=None, school_id='2565'):
    """
    Membuat screenshot PNG Penn State LionPATH (Async)
    """
    try:
        from playwright.async_api import async_playwright

        # Buat HTML dengan email
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
    # 测试代码
    import sys
    import io

    # 修复 Windows 控制台编码问题
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("测试 PSU 图片生成...")

    first_name = "John"
    last_name = "Smith"

    print(f"姓名: {first_name} {last_name}")
    print(f"PSU ID: {generate_psu_id()}")
    print(f"邮箱: {generate_psu_email(first_name, last_name)}")

    try:
        import asyncio
        img_data = asyncio.run(generate_image(first_name, last_name))

        # 保存测试图片
        with open('test_psu_card.png', 'wb') as f:
            f.write(img_data)

        print(f"✓ 图片生成成功! 大小: {len(img_data)} bytes")
        print("✓ 已保存为 test_psu_card.png")

    except Exception as e:
        print(f"✗ 错误: {e}")