import requests
from django.core.cache import cache
from .forms import ContactForm
from .models import ContactStatusChoices


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
HEADERS = {"User-Agent": "ContactManager/1.0 (recruitment task)"}

WEATHER_CACHE_TIMEOUT = 60 * 30    # 30 minutes



def get_coordinates(city):
    """Return (lat, lon) tuple for a city name, or None if not found."""
    cache_key = f"geo:{city.strip().lower()}"

    # 1. Try the cache first
    coords = cache.get(cache_key)
    if coords is not None:
        return coords

    # 2. Cache miss -> ask Nominatim
    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": city, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    if not data:  # empty list = city not found
        return None

    coords = (float(data[0]["lat"]), float(data[0]["lon"]))

    # 3. Store for next time
    cache.set(cache_key, coords, None)
    return coords    


def get_weather(city):
    """Return dict with temperature, humidity, wind speed for a city, or None."""
    cache_key = f"weather:{city.strip().lower()}"
    
    weather = cache.get(cache_key)
    if weather is not None:
        return weather
    
    coords = get_coordinates(city)
    if coords is None:
        return None
    
    try:
        response = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": coords[0],
                "longitude": coords[1],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
            headers=HEADERS,
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"DEBUG geo error: {e}")
        return None
    
    weather = {
        "temperature": data["current"]["temperature_2m"],
        "humidity": data["current"]["relative_humidity_2m"],
        "wind_speed": data["current"]["wind_speed_10m"],
    }
    
    cache.set(cache_key, weather, WEATHER_CACHE_TIMEOUT)
    
    return weather
    

def import_contacts_from_rows(rows):
    """Validate and save contacts from an iterable of dict rows.
    Returns (imported_count, error_line_numbers).
    """
    
    counter = 0
    errors = []
    for line_number, row in enumerate(rows, start=2):  # Start at 2 because the first line is the header
        # Translate the CSV row to a dictionary suitable for the ContactForm
        status_name = (row.get('status') or '').strip()
        status = ContactStatusChoices.objects.filter(name__iexact=status_name).first()
        row['status'] = status.id if status else None
        
        form = ContactForm(row)
        if form.is_valid():
            form.save()
            counter += 1
        else:
            errors.append(line_number)

    return counter, errors
