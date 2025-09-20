import json
from pathlib import Path
from story_event_card_generator import StoryEventCardGenerator
from event_card_generator import EventCardGenerator
from hipanie_event_card.story_motivation_card_generator import (
    StoryMotivationCardGenerator,
)
from hipanie_event_card.motivation_card_generator import MotivationCardGenerator
from datetime import datetime, timedelta
from weather_service import WeatherService

BASE_DIR = Path(__file__).parent
IMAGE_FOLDER = BASE_DIR.joinpath("images")
INPUT_FOLDER = BASE_DIR.joinpath("input")

FR_MONTHS = {
    "January": "Janvier",
    "February": "Février",
    "March": "Mars",
    "April": "Avril",
    "May": "Mai",
    "June": "Juin",
    "July": "Juillet",
    "August": "Août",
    "September": "Septembre",
    "October": "Octobre",
    "November": "Novembre",
    "December": "Décembre",
}

FR_MONTHS_SHORT = {
    "January": "Janv.",
    "February": "Févr.",
    "March": "Mars.",
    "April": "Avril.",
    "May": "Mai.",
    "June": "Juin.",
    "July": "Juillet.",
    "August": "Août.",
    "September": "Sept.",
    "October": "Oct.",
    "November": "Nov.",
    "December": "Déc.",
}

FR_DAYS = {
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche",
}

ES_DAYS = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

# Weekly motivation messages mapping based on the images
WEEKLY_MESSAGES = {
    "Monday": {
        "spanish_text": "Tu semana comienza aquí",
        "french_text": "Votre semaine commence ici",
        "emoji": "😄",
    },
    "Tuesday": {
        "spanish_text": "Porque hoy es un nuevo día",
        "french_text": "parce qu'aujourd'hui c'est un nouveau jour",
        "emoji": "🦊",
    },
    "Wednesday": {
        "spanish_text": "maneras de motivarte entre semana",
        "french_text": "Façons de vous motiver pendant la semaine",
        "emoji": "🐹",
    },
    "Thursday": {
        "spanish_text": "Mira la agenda de hoy",
        "french_text": "regarde l'agenda d'aujourd'hui",
        "emoji": "🐰",
    },
    "Friday": {
        "spanish_text": "Hoy es viernes de salir.",
        "french_text": "Aujourd'hui, c'est vendredi, jour de sortie",
        "emoji": "🦁",
    },
    "Saturday": {
        "spanish_text": "¿Qué hacer este sábado?",
        "french_text": "Que faire ce samedi ?",
        "emoji": "🐶",
    },
    "Sunday": {
        "spanish_text": "Diviértete este domingo",
        "french_text": "Amusez-vous bien ce dimanche !",
        "emoji": "🐸",
    },
}


# Add your OpenWeatherMap API key here
WEATHER_API_KEY = (
    "your_openweathermap_api_key_here"  # Get from https://openweathermap.org/api
)

# City mapping for weather
CITY_MAPPING = {"paris": "Paris,FR", "nantes": "Nantes,FR"}

start_date = datetime.now()
weather_service = (
    WeatherService(WEATHER_API_KEY)
    if WEATHER_API_KEY != "your_openweathermap_api_key_here"
    else None
)

data_cards = [
    {
        "datetime": single_date,
        "date": f"{single_date.day} {FR_MONTHS[single_date.strftime('%B')].upper()}",
        "day_name_es": ES_DAYS[single_date.strftime("%A")],
        "day_name_fr": FR_DAYS[single_date.strftime("%A")],
        **WEEKLY_MESSAGES[single_date.strftime("%A")],
    }
    for single_date in (start_date + timedelta(n) for n in range(8))
]

# Create images folder if it doesn't exist
if not IMAGE_FOLDER.exists():
    IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)

with INPUT_FOLDER.joinpath("events.json").open("r", encoding="utf-8") as f:
    events = json.load(f)

# Generate cards in different sizes
image_sizes = [(1080, 1350), (1080, 1920)]
for i, event in enumerate(events):
    for width, height in image_sizes:
        if height >= 1900:  # Story format
            generator = StoryEventCardGenerator(width, height)
            generator.create_event_card(
                event,
                IMAGE_FOLDER.joinpath(f"story_event_card_{i}_{width}x{height}.jpg"),
            )
        else:  # Standard format
            generator = EventCardGenerator(width, height)
            generator.create_event_card(
                event,
                IMAGE_FOLDER.joinpath(f"output_event_card_{i}_{width}x{height}.jpg"),
            )

# Weekly motivation cards generation
generator = StoryMotivationCardGenerator(1080, 1920)
for city in ["paris", "nantes"]:
    for card_data in data_cards:
        # Add weather data for each city and date
        if weather_service:
            weather_data = weather_service.get_weather_for_city(
                CITY_MAPPING[city], card_data["datetime"]
            )
            card_data["weather"] = weather_data

        output_path = IMAGE_FOLDER.joinpath(
            f"motivation_card_{city}_{generator.card_width}_{generator.card_height}_{card_data['date']}.png"
        )
        generator.create_motivation_card(
            card_data, output_path, INPUT_FOLDER.joinpath(f"{city}_logo.png")
        )


generator = MotivationCardGenerator(1080, 1350)
for city in ["paris", "nantes"]:
    for card_data in data_cards:
        single_date = card_data["datetime"]
        card_data["spanish_text"] = (
            f"¿Qué hacer en {city.capitalize()} este {card_data['day_name_es']}?"
        )
        card_data["french_text"] = (
            f"Quoi faire à {city.capitalize()} ce {card_data['day_name_fr']} ?"
        )
        card_data["emoji"] = "💃"
        card_data["date"] = (
            f"{FR_MONTHS_SHORT[single_date.strftime('%B')]}\n  {single_date.day} "
        )

        # Add weather data for each city and date
        if weather_service:
            weather_data = weather_service.get_weather_for_city(
                CITY_MAPPING[city], card_data["datetime"]
            )
            card_data["weather"] = weather_data

        output_path = IMAGE_FOLDER.joinpath(
            f"motivation_card_{city}_{generator.card_width}_{generator.card_height}_{card_data['date']}.png"
        )
        generator.create_motivation_card(
            card_data, output_path, INPUT_FOLDER.joinpath(f"{city}_logo.png")
        )
