"""Pembuatan Dokumen Bukti Guru (PDF + PNG)"""
import random
from datetime import datetime
from io import BytesIO
from pathlib import Path

from xhtml2pdf import pisa


def _render_template(first_name: str, last_name: str) -> str:
    """Baca template, ganti nama/nomor karyawan/tanggal, dan expand variabel CSS."""
    full_name = f"{first_name} {last_name}"
    employee_id = random.randint(1000000, 9999999)
    current_date = datetime.now().strftime("%m/%d/%Y %I:%M %p")

    template_path = Path(__file__).parent / "card-temp.html"
    html = template_path.read_text(encoding="utf-8")

    # Expand variabel CSS, kompatibel dengan xhtml2pdf
    color_map = {
        "var(--primary-blue)": "#0056b3",
        "var(--border-gray)": "#dee2e6",
        "var(--bg-gray)": "#f8f9fa",
    }
    for placeholder, color in color_map.items():
        html = html.replace(placeholder, color)

    # Ganti nama contoh / nomor karyawan / tanggal (template ada 2 tempat nama + span)
    html = html.replace("Sarah J. Connor", full_name)
    html = html.replace("E-9928104", f"E-{employee_id}")
    html = html.replace('id="currentDate"></span>', f'id="currentDate">{current_date}</span>')

    return html


def generate_teacher_pdf(first_name: str, last_name: str) -> bytes:
    """Membuat byte dokumen PDF bukti guru."""
    html = _render_template(first_name, last_name)

    output = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=output, encoding="utf-8")
    if pisa_status.err:
        raise Exception("Gagal membuat PDF")

    pdf_data = output.getvalue()
    output.close()
    return pdf_data


async def generate_teacher_png(first_name: str, last_name: str) -> bytes:
    """Membuat PNG menggunakan screenshot Playwright (Async)."""
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Perlu menginstal playwright, jalankan `pip install playwright` lalu `playwright install chromium`"
        ) from exc

    html = _render_template(first_name, last_name)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.new_page(viewport={"width": 1200, "height": 1000})
        await page.set_content(html, wait_until="load")
        await page.wait_for_timeout(500)  # Biarkan style stabil
        # Cari elemen .browser-mockup, jika tidak ketemu screenshot full page
        try:
            card = page.locator(".browser-mockup")
            await card.wait_for(state="visible", timeout=3000)
            png_bytes = await card.screenshot(type="png")
        except Exception:
            png_bytes = await page.screenshot(type="png", full_page=True)
            
        await browser.close()

    return png_bytes


# Kompatibilitas pemanggilan lama: default buat PDF
def generate_teacher_image(first_name: str, last_name: str) -> bytes:
    return generate_teacher_pdf(first_name, last_name)
