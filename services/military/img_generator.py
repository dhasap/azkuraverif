"""Modul Pembuatan Dokumen Militer (DD-214)"""
import random
from datetime import datetime

def generate_dd214_html(first_name, last_name, birth_date, discharge_date, branch):
    """
    Membuat HTML simulasi DD Form 214 (Certificate of Release or Discharge from Active Duty)
    """
    full_name = f"{last_name}, {first_name} {random.choice(['A.', 'J.', 'M.', 'L.'])}"
    ssn = f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"
    
    # Konversi format tanggal
    dob_obj = datetime.strptime(birth_date, "%Y-%m-%d")
    dob_str = dob_obj.strftime("%Y %b %d").upper()
    
    dis_obj = datetime.strptime(discharge_date, "%Y-%m-%d")
    dis_str = dis_obj.strftime("%Y %b %d").upper()
    
    entry_obj = datetime.strptime(f"{dis_obj.year - 4}-{dis_obj.month}-{dis_obj.day}", "%Y-%m-%d") # Asumsi 4 tahun service
    entry_str = entry_obj.strftime("%Y %b %d").upper()
    
    pay_grade = random.choice(['E-4', 'E-5', 'E-6'])
    
    branches_map = {
        'ARMY': 'ARMY',
        'NAVY': 'NAVY',
        'AIR_FORCE': 'AIR FORCE',
        'MARINES': 'MARINE CORPS',
        'COAST_GUARD': 'COAST GUARD',
        'SPACE_FORCE': 'SPACE FORCE',
        'ARMY_NATIONAL_GUARD': 'ARMY NATIONAL GUARD',
        'AIR_NATIONAL_GUARD': 'AIR NATIONAL GUARD',
        'ARMY_RESERVE': 'ARMY RESERVE',
        'NAVY_RESERVE': 'NAVY RESERVE',
        'AIR_FORCE_RESERVE': 'AIR FORCE RESERVE',
        'MARINE_CORPS_RESERVE': 'MARINE CORPS RESERVE',
        'COAST_GUARD_RESERVE': 'COAST GUARD RESERVE'
    }
    branch_str = branches_map.get(branch, 'ARMY').upper()
    
    departments_map = {
        'ARMY': 'DEPARTMENT OF THE ARMY',
        'NAVY': 'DEPARTMENT OF THE NAVY',
        'AIR_FORCE': 'DEPARTMENT OF THE AIR FORCE',
        'MARINES': 'DEPARTMENT OF THE NAVY - USMC',
        'COAST_GUARD': 'DEPARTMENT OF HOMELAND SECURITY',
        'SPACE_FORCE': 'DEPARTMENT OF THE AIR FORCE', # Space Force is under AF
        'ARMY_NATIONAL_GUARD': 'DEPARTMENT OF THE ARMY',
        'AIR_NATIONAL_GUARD': 'DEPARTMENT OF THE AIR FORCE',
        'ARMY_RESERVE': 'DEPARTMENT OF THE ARMY',
        'NAVY_RESERVE': 'DEPARTMENT OF THE NAVY',
        'AIR_FORCE_RESERVE': 'DEPARTMENT OF THE AIR FORCE',
        'MARINE_CORPS_RESERVE': 'DEPARTMENT OF THE NAVY',
        'COAST_GUARD_RESERVE': 'DEPARTMENT OF HOMELAND SECURITY'
    }
    dept_header = departments_map.get(branch, 'DEPARTMENT OF THE ARMY')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DD Form 214</title>
    <style>
        body {{
            font-family: "Courier New", Courier, monospace;
            background: #fff;
            padding: 40px;
            color: #000;
        }}
        .doc-container {{
            width: 1000px;
            border: 2px solid #000;
            padding: 5px;
            margin: 0 auto;
            position: relative;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 5px;
            margin-bottom: 5px;
        }}
        .header h1 {{ margin: 5px 0; font-size: 18px; font-weight: bold; }}
        .header h2 {{ margin: 0; font-size: 14px; font-weight: bold; }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            border: 1px solid #000;
        }}
        .cell {{
            border-right: 1px solid #000;
            border-bottom: 1px solid #000;
            padding: 2px 5px;
            font-size: 11px;
            min-height: 25px;
        }}
        .label {{ font-size: 8px; font-weight: bold; display: block; }}
        .value {{ font-size: 12px; font-weight: bold; font-family: "Courier New", monospace; }}
        
        .span-2 {{ grid-column: span 2; }}
        .span-3 {{ grid-column: span 3; }}
        .span-4 {{ grid-column: span 4; }}
        .span-6 {{ grid-column: span 6; }}
        .span-12 {{ grid-column: span 12; border-right: none; }}

        .watermark {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 150px;
            color: rgba(0,0,0,0.05);
            font-weight: bold;
            z-index: 0;
            pointer-events: none;
        }}
        
        @media print {{
            body {{ padding: 0; }}
            .doc-container {{ width: 100%; border: none; }}
        }}
    </style>
</head>
<body>

<div class="doc-container">
    <div class="watermark">COPY 4</div>
    <div class="header">
        <h2>CERTIFICATE OF RELEASE OR DISCHARGE FROM ACTIVE DUTY</h2>
        <h1>{dept_header}</h1>
    </div>
    
    <div class="grid">
        <!-- Row 1 -->
        <div class="cell span-6">
            <span class="label">1. NAME (Last, First, Middle)</span>
            <span class="value">{full_name.upper()}</span>
        </div>
        <div class="cell span-3">
            <span class="label">2. DEPARTMENT, COMPONENT AND BRANCH</span>
            <span class="value">{branch_str} - REGULAR</span>
        </div>
        <div class="cell span-3" style="border-right:none;">
            <span class="label">3. SOCIAL SECURITY NUMBER</span>
            <span class="value">{ssn}</span>
        </div>

        <!-- Row 2 -->
        <div class="cell span-4">
            <span class="label">4.a. GRADE, RATE OR RANK</span>
            <span class="value">{pay_grade}</span>
        </div>
        <div class="cell span-4">
            <span class="label">4.b. PAY GRADE</span>
            <span class="value">{pay_grade}</span>
        </div>
        <div class="cell span-4" style="border-right:none;">
            <span class="label">5. DATE OF BIRTH (YYYY MM DD)</span>
            <span class="value">{dob_str}</span>
        </div>

        <!-- Row 3 -->
        <div class="cell span-6">
            <span class="label">6. RESERVE OBLIG. TERM. DATE</span>
            <span class="value">N/A</span>
        </div>
        <div class="cell span-6" style="border-right:none;">
            <span class="label">7.a. PLACE OF ENTRY INTO ACTIVE DUTY</span>
            <span class="value">MEPS LOS ANGELES, CA</span>
        </div>

        <!-- Row 4 -->
        <div class="cell span-6">
            <span class="label">8.a. LAST DUTY ASSIGNMENT AND MAJOR COMMAND</span>
            <span class="value">HHC 1ST BATTALION, 5TH INFANTRY</span>
        </div>
        <div class="cell span-6" style="border-right:none;">
            <span class="label">8.b. STATION WHERE SEPARATED</span>
            <span class="value">FORT CARSON, CO</span>
        </div>

        <!-- Service Data Table -->
        <div class="cell span-12">
            <span class="label">9. COMMAND TO WHICH TRANSFERRED</span>
            <span class="value">USAR CONTROL GROUP (REINFORCEMENT)</span>
        </div>
        
        <div class="cell span-12">
            <span class="label">11. PRIMARY SPECIALTY (List number, title and years and months in specialty.)</span>
            <span class="value">11B INFANTRYMAN -- 4 YRS 0 MOS</span>
        </div>

        <!-- Dates -->
        <div class="cell span-6">
            <span class="label">12. RECORD OF SERVICE</span>
            <div style="display:grid; grid-template-columns: 1fr 100px;">
                <span class="label">a. DATE ENTERED AD THIS PERIOD</span>
                <span class="value" style="text-align:right;">{entry_str}</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 100px;">
                <span class="label">b. SEPARATION DATE THIS PERIOD</span>
                <span class="value" style="text-align:right;">{dis_str}</span>
            </div>
        </div>
        <div class="cell span-6" style="border-right:none;">
            <span class="label">13. DECORATIONS, MEDALS, BADGES, CITATIONS</span>
            <span class="value">ARMY COMMENDATION MEDAL // NATIONAL DEFENSE SERVICE MEDAL // GLOBAL WAR ON TERRORISM SERVICE MEDAL // ARMY SERVICE RIBBON</span>
        </div>
        
        <div class="cell span-12">
            <span class="label">14. MILITARY EDUCATION</span>
            <span class="value">BASIC COMBAT TRAINING, 10 WEEKS // INFANTRY ADVANCED INDIVIDUAL TRAINING, 6 WEEKS</span>
        </div>

        <div class="cell span-12">
            <span class="label">23. TYPE OF SEPARATION</span>
            <span class="value">DISCHARGE</span>
        </div>
        <div class="cell span-12" style="border-right:none;">
            <span class="label">24. CHARACTER OF SERVICE (Includes upgrades)</span>
            <span class="value">HONORABLE</span>
        </div>
        <div class="cell span-12" style="border-right:none;">
            <span class="label">28. NARRATIVE REASON FOR SEPARATION</span>
            <span class="value">COMPLETION OF REQUIRED ACTIVE SERVICE</span>
        </div>

    </div>
    
    <div style="margin-top:20px; text-align:center; font-size:10px; font-weight:bold;">
        DD FORM 214, FEB 2000 (PREVIOUS EDITIONS ARE OBSOLETE.)
    </div>
</div>

</body>
</html>
"""
    return html


async def generate_military_png(first_name, last_name, birth_date, discharge_date, branch):
    """
    Membuat PNG DD-214 (Async)
    """
    try:
        from playwright.async_api import async_playwright
        
        html_content = generate_dd214_html(first_name, last_name, birth_date, discharge_date, branch)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            # Viewport A4 aspect ratio approx
            page = await browser.new_page(viewport={'width': 1200, 'height': 1500})
            await page.set_content(html_content, wait_until='load')
            
            # Screenshot elemen doc-container saja agar rapi
            try:
                locator = page.locator('.doc-container')
                await locator.wait_for(state='visible')
                screenshot_bytes = await locator.screenshot(type='png')
            except:
                screenshot_bytes = await page.screenshot(type='png', full_page=True)
                
            await browser.close()
            
        return screenshot_bytes

    except ImportError:
        raise Exception("Perlu install playwright")
    except Exception as e:
        raise Exception(f"Gagal membuat dokumen militer: {str(e)}")

if __name__ == '__main__':
    # Test
    import asyncio
    async def test():
        data = await generate_military_png("JOHN", "DOE", "1990-05-20", "2024-01-15", "ARMY")
        with open("test_dd214.png", "wb") as f:
            f.write(data)
        print("Done")
    
    asyncio.run(test())
