import re
import json
from datetime import datetime

def parse_date(date_str):
    if not date_str: return None
    # Remove markdown bold/etc
    clean = date_str.replace('*', '').strip()
    try:
        return datetime.strptime(clean, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None

def normalize_branch(branch_text):
    if not branch_text: return None
    text = branch_text.upper()
    if "AIR FORCE" in text or "ARMY AIR" in text:
        return "AIR_FORCE"
    if "MARINE" in text:
        return "MARINES"
    if "COAST GUARD" in text:
        return "COAST_GUARD"
    if "NAVY" in text:
        return "NAVY"
    if "ARMY" in text:
        return "ARMY"
    if "SPACE FORCE" in text:
        return "SPACE_FORCE"
    return None

def parse_veterans(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    records = []
    current_record = {}
    
    # State machine
    expecting_value_for = None
    
    for line in lines:
        raw_line = line.strip()
        # Clean markdown table chars
        clean_line = raw_line.replace('|', '').replace('*', '').strip()
        
        if not clean_line: continue

        # Check for Key: Value on same line
        if "Name:" in clean_line:
            # Save previous
            if current_record.get('first_name') and current_record.get('last_name') and \
               current_record.get('birth_date') and current_record.get('discharge_date') and \
               current_record.get('branch'):
                records.append(current_record)
            
            current_record = {}
            
            parts = clean_line.split("Name:", 1)
            val = parts[1].strip()
            if val:
                # Value on same line
                process_name(val, current_record)
            else:
                expecting_value_for = 'name'

        elif "Rank & Branch:" in clean_line:
            parts = clean_line.split(":", 1)
            val = parts[1].strip()
            if val:
                current_record['branch'] = normalize_branch(val)
            else:
                expecting_value_for = 'branch'

        elif "Date of Birth:" in clean_line:
            parts = clean_line.split(":", 1)
            val = parts[1].strip()
            if val:
                current_record['birth_date'] = parse_date(val)
            else:
                expecting_value_for = 'dob'

        elif "Date of Death:" in clean_line:
            parts = clean_line.split(":", 1)
            val = parts[1].strip()
            if val:
                current_record['discharge_date'] = parse_date(val)
            else:
                expecting_value_for = 'dod'
        
        elif expecting_value_for:
            # We are on the next line and expected a value
            if expecting_value_for == 'name':
                process_name(clean_line, current_record)
            elif expecting_value_for == 'branch':
                current_record['branch'] = normalize_branch(clean_line)
            elif expecting_value_for == 'dob':
                current_record['birth_date'] = parse_date(clean_line)
            elif expecting_value_for == 'dod':
                current_record['discharge_date'] = parse_date(clean_line)
            
            expecting_value_for = None # Reset

    # Add last
    if current_record.get('first_name') and current_record.get('last_name') and \
       current_record.get('birth_date') and current_record.get('discharge_date') and \
       current_record.get('branch'):
        records.append(current_record)

    return records

def process_name(name_str, record):
    # ALVIN, ALLAN W
    # YORK, A HUDDLESTON
    if "," in name_str:
        last, first = name_str.split(",", 1)
        record['last_name'] = last.strip().title()
        # Take first part of first name (remove middle initials)
        f_parts = first.strip().split()
        if f_parts:
            record['first_name'] = f_parts[0].title()
    else:
        # Fallback
        parts = name_str.split()
        if len(parts) >= 2:
            record['first_name'] = parts[0].title()
            record['last_name'] = parts[-1].title()

if __name__ == "__main__":
    vets = parse_veterans("Data veteran.md")
    print(f"Found {len(vets)} valid records.")
    
    with open("data/veterans.json", "w") as f:
        json.dump(vets, f, indent=2)
    print("Saved to data/veterans.json")