import requests
from datetime import datetime

def get_latest_powerball(return_with_date=False):
    url = "https://data.ny.gov/resource/d6yy-54nr.json?$order=draw_date DESC&$limit=1"
    response = requests.get(url)
    data = response.json()

    if not data:
        raise ValueError("No Powerball data found.")

    numbers = list(map(int, data[0]["winning_numbers"].split()))
    main_numbers = numbers[:5]
    power_ball = numbers[5]
    draw_date = datetime.strptime(data[0]["draw_date"][:10], "%Y-%m-%d").date()

    if return_with_date:
        return (main_numbers, power_ball), draw_date
    return main_numbers, power_ball

def get_latest_megamillions(return_with_date=False):
    url = "https://data.ny.gov/resource/5xaw-6ayf.json?$order=draw_date DESC&$limit=1"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()

    if not data or "winning_numbers" not in data[0]:
        raise ValueError("No Mega Millions results found or missing fields.")

    numbers = list(map(int, data[0]["winning_numbers"].split()))
    mega_ball = int(data[0]["mega_ball"])
    draw_date = data[0]["draw_date"][:10]  # Format: YYYY-MM-DD

    if return_with_date:
        return (numbers, mega_ball), draw_date
    return numbers, mega_ball
