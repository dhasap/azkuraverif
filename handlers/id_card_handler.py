"""
Handler untuk fitur ID card generator
"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from services.id_card_generator.id_card_generator import generate_id_card
import os

router = Router()

# Definisikan state untuk proses pembuatan ID card
class IDCardStates(StatesGroup):
    waiting_for_card_type = State()
    waiting_for_name = State()
    waiting_for_institution = State()
    waiting_for_id_number = State()
    waiting_for_photo = State()
    waiting_for_rank = State()  # Khusus untuk ID militer


@router.message(Command("create_id"))
async def cmd_create_id(message: types.Message, state: FSMContext):
    """Perintah untuk memulai pembuatan ID card"""
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Student ID", callback_data="id_type:student")],
        [types.InlineKeyboardButton(text="Teacher ID", callback_data="id_type:teacher")],
        [types.InlineKeyboardButton(text="Military ID", callback_data="id_type:military")],
    ])
    
    await message.answer(
        "Select the type of ID card you want to create:",
        reply_markup=keyboard
    )
    await state.set_state(IDCardStates.waiting_for_card_type)


@router.callback_query(lambda c: c.data.startswith("id_type:"))
async def process_id_type_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """Proses pemilihan tipe ID card"""
    await callback_query.answer()
    
    card_type = callback_query.data.split(":")[1]
    await state.update_data(card_type=card_type)
    
    await callback_query.message.answer("Please enter the name for the ID card:")
    await state.set_state(IDCardStates.waiting_for_name)


@router.message(IDCardStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    """Proses input nama"""
    await state.update_data(name=message.text)
    
    data = await state.get_data()
    card_type = data.get("card_type")
    
    if card_type == "military":
        await message.answer("Please enter the military branch (e.g., Army, Navy, Air Force):")
        await state.set_state(IDCardStates.waiting_for_institution)
    else:
        await message.answer("Please enter the institution or organization name:")
        await state.set_state(IDCardStates.waiting_for_institution)


@router.message(IDCardStates.waiting_for_institution)
async def process_institution(message: types.Message, state: FSMContext):
    """Proses input institusi"""
    await state.update_data(institution=message.text)
    
    data = await state.get_data()
    card_type = data.get("card_type")
    
    if card_type == "military":
        await message.answer("Please enter the rank (e.g., Sergeant, Captain):")
        await state.set_state(IDCardStates.waiting_for_rank)
    else:
        await message.answer("Please enter the ID number:")
        await state.set_state(IDCardStates.waiting_for_id_number)


@router.message(IDCardStates.waiting_for_rank)
async def process_rank(message: types.Message, state: FSMContext):
    """Proses input pangkat (khusus militer)"""
    await state.update_data(rank=message.text)
    
    await message.answer("Please enter the military ID number:")
    await state.set_state(IDCardStates.waiting_for_id_number)


@router.message(IDCardStates.waiting_for_id_number)
async def process_id_number(message: types.Message, state: FSMContext):
    """Proses input nomor ID"""
    await state.update_data(id_number=message.text)
    
    await message.answer(
        "Please send a photo to be used on the ID card (optional). "
        "Send 'skip' if you don't want to add a photo."
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
    elif message.text and message.text.lower() == "skip":
        # Pengguna memilih untuk tidak menambahkan foto
        pass
    else:
        await message.answer(
            "Please send a photo or type 'skip' to continue without a photo."
        )
        return
    
    # Siapkan data untuk membuat ID card
    final_id_number = id_number
    if card_type == "military":
        final_id_number = {"rank": rank, "military_id": id_number}
    
    try:
        # Generate ID card
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
                caption=f"Your {card_type.replace('_', ' ').title()} ID Card is ready!"
            )
        
        # Hapus file foto sementara jika ada
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)
        
        # Reset state
        await state.clear()
        
    except Exception as e:
        await message.answer(f"An error occurred while creating the ID card: {str(e)}")
        await state.clear()