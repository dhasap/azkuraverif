"""
Handler untuk fitur ID card generator
Mendukung pembuatan ID card dengan data manual atau otomatis
"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from services.id_card_generator.id_card_generator import generate_id_card, generate_auto_id_card
import os

router = Router()

# Definisikan state untuk proses pembuatan ID card
class IDCardStates(StatesGroup):
    waiting_for_card_type = State()
    waiting_for_generation_method = State()  # Manual atau otomatis
    waiting_for_name = State()
    waiting_for_institution = State()
    waiting_for_id_number = State()
    waiting_for_photo = State()
    waiting_for_rank = State()  # Khusus untuk ID militer


@router.message(Command("create_id"))
async def cmd_create_id(message: types.Message, state: FSMContext):
    """Perintah untuk memulai pembuatan ID card"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎓 Student ID", callback_data="id_type:student")],
        [types.InlineKeyboardButton(text="👨‍🏫 Teacher ID", callback_data="id_type:teacher")],
        [types.InlineKeyboardButton(text="🎖️ Military ID", callback_data="id_type:military")],
    ])

    await message.answer(
        "💳 <b>ID CARD GENERATOR</b>\n"
        "Pilih jenis ID card yang ingin Anda buat:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(IDCardStates.waiting_for_card_type)


@router.callback_query(lambda c: c.data.startswith("id_type:"))
async def process_id_type_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Proses pemilihan tipe ID card dan metode pembuatan"""
    await callback_query.answer()

    card_type = callback_query.data.split(":")[1]
    await state.update_data(card_type=card_type)

    # Tanyakan apakah ingin menggunakan data otomatis atau manual
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🤖 Generate Otomatis", callback_data="gen:auto")],
        [types.InlineKeyboardButton(text="✏️ Masukkan Manual", callback_data="gen:manual")],
    ])

    await callback_query.message.edit_text(
        f"Anda memilih <b>{card_type.title()} ID</b>.\n\n"
        "Pilih metode pembuatan:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(IDCardStates.waiting_for_generation_method)


@router.callback_query(lambda c: c.data.startswith("gen:"))
async def process_generation_method(callback_query: types.CallbackQuery, state: FSMContext):
    """Proses pemilihan metode pembuatan (otomatis atau manual)"""
    await callback_query.answer()

    method = callback_query.data.split(":")[1]
    await state.update_data(method=method)

    # Jika metode otomatis, langsung generate dan kirim
    if method == "auto":
        data = await state.get_data()
        card_type = data.get("card_type")

        try:
            # Generate ID card otomatis
            id_card_path = generate_auto_id_card(card_type=card_type)

            # Kirim ID card ke pengguna
            with open(id_card_path, 'rb') as photo_file:
                await callback_query.message.answer_photo(
                    photo=types.FSInputFile(id_card_path),
                    caption=f"💳 <b>{card_type.replace('_', ' ').title()} ID Card Otomatis</b>\n"
                            f"Berikut adalah ID card yang dibuat secara otomatis."
                )

            # Reset state
            await state.clear()

        except Exception as e:
            await callback_query.message.answer(f"❌ Terjadi kesalahan saat membuat ID card: {str(e)}")
            await state.clear()
    else:
        # Metode manual, lanjutkan ke input data
        await callback_query.message.edit_text("Silakan masukkan nama untuk ID card:")
        await state.set_state(IDCardStates.waiting_for_name)


@router.message(IDCardStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Proses input nama"""
    await state.update_data(name=message.text)

    data = await state.get_data()
    card_type = data.get("card_type")

    if card_type == "military":
        await message.answer("Silakan masukkan cabang militer (contoh: Army, Navy, Air Force):")
        await state.set_state(IDCardStates.waiting_for_institution)
    else:
        await message.answer("Silakan masukkan nama institusi atau organisasi:")
        await state.set_state(IDCardStates.waiting_for_institution)


@router.message(IDCardStates.waiting_for_institution)
async def process_institution(message: types.Message, state: FSMContext):
    """Proses input institusi"""
    await state.update_data(institution=message.text)

    data = await state.get_data()
    card_type = data.get("card_type")

    if card_type == "military":
        await message.answer("Silakan masukkan pangkat (contoh: Sergeant, Captain):")
        await state.set_state(IDCardStates.waiting_for_rank)
    else:
        await message.answer("Silakan masukkan nomor ID:")
        await state.set_state(IDCardStates.waiting_for_id_number)


@router.message(IDCardStates.waiting_for_rank)
async def process_rank(message: types.Message, state: FSMContext):
    """Proses input pangkat (khusus militer)"""
    await state.update_data(rank=message.text)

    await message.answer("Silakan masukkan nomor ID militer:")
    await state.set_state(IDCardStates.waiting_for_id_number)


@router.message(IDCardStates.waiting_for_id_number)
async def process_id_number(message: types.Message, state: FSMContext):
    """Proses input nomor ID"""
    await state.update_data(id_number=message.text)

    await message.answer(
        "📸 Silakan kirim foto untuk digunakan pada ID card (opsional).\n\n"
        "Ketik 'lewati' jika Anda tidak ingin menambahkan foto."
    )
    await state.set_state(IDCardStates.waiting_for_photo)


@router.message(IDCardStates.waiting_for_photo)
async def process_photo(message: types.Message, state: FSMContext):
    """Proses upload foto atau skip"""
    data = await state.get_data()
    card_type = data.get("card_type")
    name = data.get("name")
    institution = data.get("institution")
    id_number = data.get("id_number")
    rank = data.get("rank", "")

    photo_path = None

    # Jika pengguna mengirim foto
    if message.photo:
        # Ambil foto dengan resolusi tertinggi
        photo = message.photo[-1]
        file_id = photo.file_id

        # Dapatkan info file
        file_info = await message.bot.get_file(file_id)
        file_extension = os.path.splitext(file_info.file_path)[1]

        # Buat path lokal untuk menyimpan foto sementara
        unique_filename = f"temp_photo_{message.from_user.id}_{file_id}{file_extension}"
        photo_path = f"temp/{unique_filename}"

        # Pastikan direktori temp ada
        os.makedirs("temp", exist_ok=True)

        # Download file
        await message.bot.download_file(file_info.file_path, photo_path)
    elif message.text and message.text.lower() in ["lewati", "skip", "l"]:
        # Pengguna memilih untuk tidak menambahkan foto
        pass
    else:
        await message.answer(
            "📸 Silakan kirim foto atau ketik 'lewati' untuk melanjutkan tanpa foto."
        )
        return

    # Siapkan data untuk membuat ID card
    final_id_number = id_number
    if card_type == "military":
        final_id_number = {"rank": rank, "military_id": id_number}

    try:
        # Generate ID card dengan data manual
        id_card_path = generate_id_card(
            card_type=card_type,
            name=name,
            institution_or_branch=institution,
            id_number=final_id_number,
            photo_path=photo_path
        )

        # Kirim ID card ke pengguna
        with open(id_card_path, 'rb') as photo_file:
            await message.answer_photo(
                photo=types.FSInputFile(id_card_path),
                caption=f"💳 <b>{card_type.replace('_', ' ').title()} ID Card</b>\n"
                        f"Berikut adalah ID card Anda yang telah dibuat."
            )

        # Hapus file foto sementara jika ada
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)

        # Reset state
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Terjadi kesalahan saat membuat ID card: {str(e)}")
        await state.clear()