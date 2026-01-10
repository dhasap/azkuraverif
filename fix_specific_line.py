#!/usr/bin/env python3
"""
Perbaikan spesifik untuk baris yang bermasalah di handler verification
"""

def fix_line_in_verification():
    with open('/home/user/azkuraverif/handlers/verification.py', 'r') as f:
        lines = f.readlines()
    
    # Perbaiki baris spesifik yang bermasalah
    for i in range(len(lines)):
        if " purse Saldo Anda: <b>{user_data.get('balance', 0)} Poin</b>" in lines[i]:
            # Ganti dengan baris yang benar
            lines[i] = '            f" purse Saldo Anda: <b>{user_data.get(\'balance\', 0)} Poin</b>\\n\\n"\n'
            break
    
    # Tulis kembali file
    with open('/home/user/azkuraverif/handlers/verification.py', 'w') as f:
        f.writelines(lines)
    
    print("Perbaikan baris spesifik telah diterapkan")

if __name__ == "__main__":
    fix_line_in_verification()