import json
import logging
import argparse
from pathlib import Path
from story_event_card_generator import StoryEventCardGenerator
from event_card_generator import EventCardGenerator
from hipanie_event_card.story_motivation_card_generator import (
    StoryMotivationCardGenerator,
)
from hipanie_event_card.motivation_card_generator import MotivationCardGenerator
from find_common_events import EventMerger
from datetime import datetime, timedelta
from weather_service import WeatherService
from typing import Any

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
IMAGE_FOLDER = BASE_DIR.joinpath("images")
INPUT_FOLDER = BASE_DIR.joinpath("input")

# Create images folder if it doesn't exist
if not IMAGE_FOLDER.exists():
    IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)

CALCULATION_DATE = datetime.now()

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
        "french_text": "Parce qu'aujourd'hui c'est un nouveau jour",
        "emoji": "🦊",
    },
    "Wednesday": {
        "spanish_text": "Maneras de motivarte entre semana",
        "french_text": "Façons de vous motiver pendant la semaine",
        "emoji": "🐹",
    },
    "Thursday": {
        "spanish_text": "Mira la agenda de hoy",
        "french_text": "Regardez l'agenda d'aujourd'hui",
        "emoji": "🐰",
    },
    "Friday": {
        "spanish_text": "Hoy es viernes de salir.",
        "french_text": "Aujourd'hui, c'est vendredi, jour de sortie",
        "emoji": "🦁",
    },
    "Saturday": {
        "spanish_text": "¿Qué hacer este sábado?",
        "french_text": "Quoi faire ce samedi ?",
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


def get_next_monday(start_date: datetime) -> tuple[datetime, datetime]:
    # If start_date is already Monday, use it; otherwise calculate next Monday
    if start_date.weekday() == 0:  # Monday is 0 in weekday()
        next_monday = start_date
    else:
        days_until_monday = (7 - start_date.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = start_date + timedelta(days=days_until_monday)

    # Calculate the Sunday of that week (6 days after Monday)
    next_sunday = next_monday + timedelta(days=6)
    return next_monday, next_sunday


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments to determine which sections to run."""
    parser = argparse.ArgumentParser(
        description="Generate various types of event and motivation cards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available sections:
  1. find-common-events         Find and merge common events between detailed and non-detailed files
  2. event-cards                Generate event cards in different sizes
  3. day-motivation-cards       Generate daily motivation cards by city
  4. week-motivation-cards      Generate week motivation cards by city

Examples:
  python main.py --sections 1 3           # Run find common events and day motivation cards
  python main.py --sections find-common-events   # Run only find common events
  python main.py --sections 1             # Run only find common events
  python main.py --all                     # Run all sections (default)
        """,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--sections",
        nargs="+",
        help="Specify which sections to run. Use numbers (1-4) or names (find-common-events, event-cards, day-motivation-cards, week-motivation-cards)",
        default=None,
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run all sections (default behavior)",
        default=False,
    )

    parser.add_argument(
        "--list-sections", action="store_true", help="List available sections and exit"
    )

    return parser.parse_args()


def normalize_section_names(sections):
    """Convert section numbers or names to a standardized list."""
    section_mapping = {
        "1": "find-common-events",
        "2": "event-cards",
        "3": "day-motivation-cards",
        "4": "week-motivation-cards",
        "find-common-events": "find-common-events",
        "event-cards": "event-cards",
        "day-motivation-cards": "day-motivation-cards",
        "week-motivation-cards": "week-motivation-cards",
    }

    normalized = []
    for section in sections:
        if section in section_mapping:
            normalized.append(section_mapping[section])
        else:
            logger.warning(
                f"Unknown section: {section}. Available sections: {list(section_mapping.keys())}"
            )

    return normalized


def should_run_section(section_name: str, sections_to_run: list[str] | None) -> bool:
    """Check if a specific section should be run based on user input."""
    return sections_to_run is None or section_name in sections_to_run


def main():
    """Main function to run the card generation based on command line arguments."""
    # Parse command line arguments
    args = parse_arguments()

    # Handle list sections request
    if args.list_sections:
        print("Available sections:")
        print(
            "  1. find-common-events         Find and merge common events between detailed and non-detailed files"
        )
        print("  2. event-cards                Generate event cards in different sizes")
        print("  3. day-motivation-cards       Generate daily motivation cards by city")
        print("  4. week-motivation-cards      Generate week motivation cards by city")
        return

    # Determine which sections to run
    sections_to_run = None
    if args.sections:
        sections_to_run = normalize_section_names(args.sections)
        logger.info(f"Running sections: {sections_to_run}")
    elif not args.all:
        logger.info("Running all sections (use --sections to run specific ones)")

    weather_service = (
        WeatherService(WEATHER_API_KEY)
        if WEATHER_API_KEY != "your_openweathermap_api_key_here"
        else None
    )

    # Find Common Events
    if should_run_section("find-common-events", sections_to_run):
        run_find_common_events(["paris"])

    # Event Cards Generation
    if should_run_section("event-cards", sections_to_run):
        generate_event_cards(["paris", "nantes"])

    # Day Motivation Cards Generation
    if should_run_section("day-motivation-cards", sections_to_run):
        next_monday, _ = get_next_monday(CALCULATION_DATE)
        data_cards = [
            {
                "datetime": single_date,
                "date": f"{single_date.day} {FR_MONTHS[single_date.strftime('%B')].upper()}",
                "day_name_es": ES_DAYS[single_date.strftime("%A")],
                "day_name_fr": FR_DAYS[single_date.strftime("%A")],
                **WEEKLY_MESSAGES[single_date.strftime("%A")],
            }
            for single_date in (next_monday + timedelta(n) for n in range(7))
        ]
        generate_day_motivation_cards(["paris"], data_cards, weather_service)

    # Week Motivation Cards Generation
    if should_run_section("week-motivation-cards", sections_to_run):
        generate_week_motivation_cards(["nantes"], CALCULATION_DATE, weather_service)


def generate_event_cards(cities: list[str]):
    logger.info("Starting event card generation...")
    image_sizes = [(1080, 1350), (1080, 1920)]
    for city in cities:
        event_file_path = INPUT_FOLDER.joinpath(f"events_{city}.json")
        if not event_file_path.exists():
            logger.warning(f"Event file does not exist: {event_file_path}")
            continue

        with event_file_path.open("r", encoding="utf-8") as f:
            events = json.load(f)

        for width, height in image_sizes:
            if height >= 1900:  # Story format
                generator = StoryEventCardGenerator(width, height)
                prefix = "story"
            else:  # Standard format
                generator = EventCardGenerator(width, height)
                prefix = "standard"

            for i, event in enumerate(events):
                generator.create_event_card(
                    event,
                    IMAGE_FOLDER.joinpath(
                        f"{prefix}_event_card_{city}_{i}_{width}x{height}.jpg"
                    ),
                )

    logger.info("Event card generation completed!")


def generate_day_motivation_cards(
    cities: list[str],
    data_cards: dict[str, Any],
    weather_service: WeatherService | None = None,
):
    logger.info("Starting weekly story motivation card generation for big cities...")
    image_sizes = [(1080, 1920), (1080, 1350)]
    for city in cities:
        for width, height in image_sizes:
            if height >= 1900:  # Story format
                generator = StoryMotivationCardGenerator(width, height)
                prefix = "story"
            else:  # Standard format
                generator = MotivationCardGenerator(width, height)
                prefix = "standard"

            for card_data in data_cards:
                # Add weather data for each city and date
                if weather_service:
                    weather_data = weather_service.get_weather_for_city(
                        CITY_MAPPING[city], card_data["datetime"]
                    )
                    card_data["weather"] = weather_data

                if height == 1350:
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

                output_path = IMAGE_FOLDER.joinpath(
                    f"{prefix}_motivation_card_{city}_{generator.card_width}_{generator.card_height}_{card_data['date']}.png"
                )
                generator.create_motivation_card(
                    card_data, output_path, INPUT_FOLDER.joinpath(f"{city}_logo.jpeg")
                )
    logger.info("Weekly motivation cards generation completed!")


def generate_week_motivation_cards(
    cities: list[str], calculation_date: datetime, weather_service: WeatherService
):
    logger.info(
        "Starting weekly standard motivation card generation for small cities..."
    )
    generator = MotivationCardGenerator(1080, 1350)
    next_monday, next_sunday = get_next_monday(calculation_date)
    for city in cities:
        card_data = {
            "date": f"{FR_MONTHS[next_monday.strftime('%B')].upper()} \n {next_monday.day} - {next_sunday.day}",
            "spanish_text": f"¿Qué hacer en {city.capitalize()} esta semana ?",
            "french_text": f"Quoi faire à {city.capitalize()} cette semaine ?",
            "day_name_fr": "Semaine",
            "day_name_es": "Semana",
            "emoji": "💃",
            "datetime": next_monday,  # Add datetime for weather service
        }
        # Add weather data for each city and date
        if weather_service:
            weather_data = weather_service.get_weather_for_city(
                CITY_MAPPING[city], next_monday
            )
            card_data["weather"] = weather_data

        output_path = IMAGE_FOLDER.joinpath(
            f"standard_motivation_card_{city}_{generator.card_width}_{generator.card_height}_{card_data['date']}.png"
        )
        generator.create_motivation_card(
            card_data, output_path, INPUT_FOLDER.joinpath(f"{city}_logo.jpeg")
        )
    logger.info("Standard motivation cards for small cities generation completed!")


def run_find_common_events(cities: list[str]):
    """Run the find common events process for available cities."""
    logger.info("Starting find common events process...")

    merger = EventMerger()

    for city in cities:
        events_non_detailed_file = INPUT_FOLDER.joinpath(
            f"events_{city}_non_detailed.json"
        )
        events_detailed_file = INPUT_FOLDER.joinpath(f"events_{city}_detailed.json")
        output_file = INPUT_FOLDER.joinpath(f"events_{city}.json")

        # Check if both required files exist
        if not events_non_detailed_file.exists():
            logger.warning(
                f"Non-detailed events file does not exist: {events_non_detailed_file}"
            )
            continue

        if not events_detailed_file.exists():
            logger.warning(
                f"Detailed events file does not exist: {events_detailed_file}"
            )
            continue

        logger.info(f"Processing events for {city}...")
        merger.find_and_merge_common_events(
            events_non_detailed_file, events_detailed_file, output_file
        )

    logger.info("Find common events process completed!")


if __name__ == "__main__":
    main()
