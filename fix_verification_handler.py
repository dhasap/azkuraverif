#!/usr/bin/env python3
"""
Script untuk memperbaiki handler verification.py
"""

def fix_verification_handler():
    with open('/home/user/azkuraverif/handlers/verification.py', 'r') as f:
        lines = f.readlines()
    
    # Temukan dan perbaiki baris-baris yang bermasalah
    for i in range(len(lines)):
        # Perbaiki baris yang mengakses user_data['balance'] tanpa pengecekan
        if "if user_data['balance'] < cost:" in lines[i]:
            lines[i] = "    if not user_data or user_data.get('balance', 0) < cost:\n"
        elif " purse Saldo Anda: <b>{user_data['balance']}" in lines[i]:
            lines[i] = "            f\" purse Saldo Anda: <b>{user_data.get('balance', 0)} Poin</b>\\n\\n\"\n"
    
    # Tulis kembali file
    with open('/home/user/azkuraverif/handlers/verification.py', 'w') as f:
        f.writelines(lines)
    
    print("File verification.py telah diperbaiki")

if __name__ == "__main__":
    fix_verification_handler()