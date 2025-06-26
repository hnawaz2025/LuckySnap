import re
from datetime import datetime

def extract_draw_date(text: str) -> str | None:
    """
    Extracts draw date in various formats like:
    - 06/07/2025
    - 06-07-25
    - June 7, 2025
    Returns in ISO format: '2025-06-07'
    """
    patterns = [
        r"(\d{2}/\d{2}/\d{4})",        # MM/DD/YYYY
        r"(\d{2}-\d{2}-\d{2})",        # MM-DD-YY
        r"(\d{1,2} [A-Za-z]+ \d{4})",  
        r"([A-Za-z]+ \d{1,2}, \d{4})"]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            try:
                # Try all supported date formats
                for fmt in ["%m/%d/%Y", "%m-%d-%y", "%d %B %Y", "%B %d, %Y"]:
                    try:
                        return datetime.strptime(date_str, fmt).date().isoformat()
                    except ValueError:
                        continue
            except Exception:
                continue
    return None

def parse_powerball_ticket(ocr_text: str):
    """
    Extracts all valid Powerball lines from OCR text:
    Pattern: 5 numbers + 'PB' or 'PB:' + Powerball number
    Returns a list of dicts with 'numbers' and 'powerball'
    """
    pattern = r'(?:(\d{2})\s+){5}(PB[:\s]?)(\d{1,2})'
    matches = re.findall(pattern, ocr_text)

    parsed_lines = []
    
    for match in re.finditer(r'((?:\d{2}\s+){5})(?:PB[:\s]?)(\d{1,2})', ocr_text):
        number_str, pb = match.group(1), match.group(2)
        numbers = list(map(int, number_str.strip().split()))
        powerball = int(pb)

        # Validation
        if len(numbers) == 5 and all(1 <= n <= 69 for n in numbers) and 1 <= powerball <= 26:
            parsed_lines.append({
                "numbers": numbers,
                "powerball": powerball})

    return parsed_lines

def parse_megamillions_ticket(ocr_text: str):
    """
    Extracts all valid megamillions lines from OCR text:
    Pattern: 5 numbers + 'MB' or 'MB:' + Megaball number
    Returns a list of dicts with 'numbers' and 'megaball'
    """
    pattern = r'(?:(\d{2})\s+){5}(MB[:\s]?)(\d{1,2})'
    matches = re.findall(pattern, ocr_text)

    parsed_lines = []
    
    for match in re.finditer(r'((?:\d{2}\s+){5})(?:MB[:\s]?)(\d{1,2})', ocr_text):
        number_str, pb = match.group(1), match.group(2)
        numbers = list(map(int, number_str.strip().split()))
        megaball = int(pb)

        # Validation
        if len(numbers) == 5 and all(1 <= n <= 69 for n in numbers) and 1 <= megaball <= 26:
            parsed_lines.append({
                "numbers": numbers,
                "powerball": megaball})

    return parsed_lines

def parse_ticket(ocr_text: str, game_type: str):
    ticket_date = extract_draw_date(ocr_text)
    
    if game_type.lower() == "powerball":
        return parse_powerball_ticket(ocr_text), ticket_date
    elif game_type.lower() == "mega millions":
        return parse_megamillions_ticket(ocr_text), ticket_date
    else:
        return [], ticket_date
