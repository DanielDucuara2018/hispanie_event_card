import json
from pathlib import Path
from story_event_card_generator import StoryEventCardGenerator
from event_card_generator import EventCardGenerator

BASE_DIR = Path(__file__).parent
IMAGE_FOLDER = BASE_DIR.joinpath("images")
INPUT_FOLDER = BASE_DIR.joinpath("input")

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
