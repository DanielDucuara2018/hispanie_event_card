import json
import requests
from pilmoji import Pilmoji
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path

BASE_DIR = Path(__file__).parent
IMAGE_FOLDER = BASE_DIR.joinpath("images")
INPUT_FOLDER = BASE_DIR.joinpath("input")

# 🔹 Card size (based on your samples, WhatsApp shared images ~1080x1350)
CARD_WIDTH, CARD_HEIGHT = 1080, 1350

# 🔹 Fonts (system dependent — adapt paths if needed)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# Create images folder if it doesn't exist
if not IMAGE_FOLDER.exists():
    IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)


def load_and_process_image(event: dict[str, str]) -> Image.Image:
    """
    Load image from URL or file path and crop to show top 3/4 of the image.

    Args:
        event: Dictionary containing event data with 'image' key

    Returns:
        PIL Image object processed and ready for card
    """
    if event["image"].startswith("http"):
        response = requests.get(event["image"])
        img = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        img = Image.open(event["image"]).convert("RGB")

    # Crop image to show only the top 3/4
    img_width, img_height = img.size
    cropped_height = 3 * img_height // 4

    # If image is wider than card, also crop horizontally
    if img_width > CARD_WIDTH:
        crop_x = (img_width - CARD_WIDTH) // 2
        img = img.crop((crop_x, 0, crop_x + CARD_WIDTH, cropped_height))
    else:
        img = img.crop((0, 0, img_width, cropped_height))

    return img


def get_banner_color(date: str) -> tuple[int, int, int]:
    """
    Determine banner color based on the day of the week in the date string.

    Args:
        date: Date string containing day information

    Returns:
        RGB color tuple for the banner
    """
    day = date.upper()
    if "VENDREDI" in day or "VIERNES" in day or "FRIDAY" in day:
        return (67, 160, 71)  # Green
    elif "JEUDI" in day or "JUEVES" in day or "THURSDAY" in day:
        return (66, 165, 245)  # Blue
    elif "MERCREDI" in day or "MIERCOLES" in day or "WEDNESDAY" in day:
        return (102, 187, 106)  # Light green
    else:
        return (255, 193, 7)  # Yellow/orange


def draw_inclined_banner(
    draw: ImageDraw.Draw, banner_start_y: int, banner_color: tuple[int, int, int]
) -> int:
    """
    Draw an inclined banner rectangle on the card.

    Args:
        draw: ImageDraw object for drawing on the card
        banner_start_y: Y position where banner starts
        banner_color: RGB color tuple for the banner

    Returns:
        Y position where content should start after the banner
    """
    banner_height = 90
    margin = 40
    angle_offset = 20

    # Draw inclined rectangle as polygon
    banner_points = [
        (margin, banner_start_y + angle_offset),  # top-left (lower)
        (CARD_WIDTH - margin, banner_start_y),  # top-right (higher)
        (CARD_WIDTH - margin, banner_start_y + banner_height),  # bottom-right
        (margin, banner_start_y + banner_height + angle_offset),  # bottom-left (lower)
    ]

    draw.polygon(banner_points, fill=banner_color)

    return banner_start_y + banner_height + angle_offset + 30


def add_banner_text(card: Image.Image, date: str, banner_start_y: int):
    """
    Add centered date/time text to the banner.

    Args:
        card: PIL Image object representing the card
        date: Date string to display on banner
        banner_start_y: Y position where banner starts
    """
    draw = ImageDraw.Draw(card)
    font_banner = ImageFont.truetype(FONT_BOLD, 42)
    angle_offset = 20
    banner_height = 90

    with Pilmoji(card) as pilmoji:
        bbox = draw.textbbox((0, 0), date, font=font_banner)
        text_width = bbox[2] - bbox[0]
        text_x = (CARD_WIDTH - text_width) // 2
        text_y = banner_start_y + (banner_height - 42) // 2 + angle_offset // 2
        pilmoji.text((text_x, text_y), date, font=font_banner, fill="white")


def wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.Draw
) -> list[str]:
    """
    Wrap text to fit within specified width, limiting to 3 lines maximum.

    Args:
        text: Text to wrap
        font: Font to use for text measurement
        max_width: Maximum width in pixels
        draw: ImageDraw object for text measurement

    Returns:
        List of text lines that fit within the width
    """
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines[:3]  # Limit to 3 lines max


def add_event_type(card: Image.Image, event: dict[str, str], y_position: int) -> int:
    """
    Add event type/category with emoji to the card.

    Args:
        card: PIL Image object representing the card
        event: Dictionary containing event data
        y_position: Y position where to place the type text

    Returns:
        Y position for the next element
    """
    left_margin = 40
    font_type = ImageFont.truetype(FONT_REGULAR, 33)
    with Pilmoji(card) as pilmoji:
        pilmoji.text(
            (left_margin, y_position),
            f"🎉 {event['type']}",
            font=font_type,
            fill="black",
        )
    return y_position + 80


def add_event_title(card: Image.Image, event: dict[str, str], y_position: int) -> int:
    """
    Add event title to the card.

    Args:
        card: PIL Image object representing the card
        event: Dictionary containing event data
        y_position: Y position where to place the title

    Returns:
        Y position for the next element
    """
    left_margin = 40
    font_title = ImageFont.truetype(FONT_BOLD, 35)
    with Pilmoji(card) as pilmoji:
        pilmoji.text(
            (left_margin, y_position),
            event["title"],
            font=font_title,
            fill="black",
        )
    return y_position + 80


def add_event_description(
    card: Image.Image, event: dict[str, str], y_position: int
) -> int:
    """
    Add wrapped event description to the card.

    Args:
        card: PIL Image object representing the card
        event: Dictionary containing event data
        y_position: Y position where to place the description

    Returns:
        Y position for the next element
    """
    draw = ImageDraw.Draw(card)
    left_margin = 40
    right_margin = 40
    font_desc = ImageFont.truetype(FONT_REGULAR, 30)
    max_desc_width = CARD_WIDTH - left_margin - right_margin

    lines = wrap_text(event["description"], font_desc, max_desc_width, draw)

    with Pilmoji(card) as pilmoji:
        for i, line in enumerate(lines):
            pilmoji.text(
                (left_margin, y_position + i * 45),
                line,
                font=font_desc,
                fill="black",
            )

    return y_position + len(lines) * 45 + 80


def add_event_cost(card: Image.Image, event: dict[str, str], y_position: int) -> int:
    """
    Add event cost/pricing information to the card.

    Args:
        card: PIL Image object representing the card
        event: Dictionary containing event data
        y_position: Y position where to place the cost

    Returns:
        Y position for the next element
    """
    left_margin = 40
    font_cost = ImageFont.truetype(FONT_BOLD, 30)
    with Pilmoji(card) as pilmoji:
        pilmoji.text(
            (left_margin, y_position),
            f"🎫 {event['cost']}",
            font=font_cost,
            fill="black",
        )
    return y_position + 50


def add_separator_line(card: Image.Image, y_position: int) -> int:
    """
    Add a horizontal separator line to the card.

    Args:
        card: PIL Image object representing the card
        y_position: Y position where to place the line

    Returns:
        Y position for the next element
    """
    draw = ImageDraw.Draw(card)
    left_margin = 40
    right_margin = 40

    draw.line(
        [(left_margin, y_position), (CARD_WIDTH - right_margin, y_position)],
        fill=(200, 200, 200),
        width=2,
    )
    return y_position + 30


def add_event_location(
    card: Image.Image, event: dict[str, str], y_position: int
) -> int:
    """
    Add event location to the card.

    Args:
        card: PIL Image object representing the card
        event: Dictionary containing event data
        y_position: Y position where to place the location

    Returns:
        Y position for the next element
    """
    left_margin = 40
    font_location = ImageFont.truetype(FONT_REGULAR, 30)
    with Pilmoji(card) as pilmoji:
        pilmoji.text(
            (left_margin, y_position),
            f"📍 {event['location']}",
            font=font_location,
            fill="black",
        )
    return y_position + 50


def add_event_content(card: Image.Image, event: dict[str, str], content_start_y: int):
    """
    Add all event content (type, title, description, cost, location) to the card.

    Args:
        card: PIL Image object representing the card
        event: Dictionary containing event data
        content_start_y: Y position where content should start
    """
    y_pos = content_start_y + 20  # Small padding from banner

    y_pos = add_event_type(card, event, y_pos)
    y_pos = add_event_title(card, event, y_pos)
    y_pos = add_event_description(card, event, y_pos)
    y_pos = add_event_cost(card, event, y_pos)
    y_pos = add_separator_line(card, y_pos)
    add_event_location(card, event, y_pos)


def create_event_card(event: dict[str, str], output_path: str):
    """
    Create an event card with standardized design matching reference images.

    Args:
        event: Dictionary containing event data (image, date, type, title, description, cost, location)
        output_path: Path where the generated card image should be saved
    """
    # Create base card
    card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "white")
    draw = ImageDraw.Draw(card)

    # Load and process event image
    img = load_and_process_image(event)
    img_x = (CARD_WIDTH - img.width) // 2
    card.paste(img, (img_x, 0))

    # Draw inclined banner
    banner_start_y = img.height
    banner_color = get_banner_color(event["date"])
    content_start_y = draw_inclined_banner(draw, banner_start_y, banner_color)

    # Add banner text
    add_banner_text(card, event["date"], banner_start_y)

    # Add event content
    add_event_content(card, event, content_start_y)

    # Save the card
    card.save(output_path, quality=95)
    print(f"✅ Saved card at {output_path}")


if __name__ == "__main__":
    """
    # Example JSON input
    event_json = {
        "image": "https://scontent.fcdg4-1.fna.fbcdn.net/v/t39.30808-6/520225612_1287586610043747_9068125171068301630_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=75d36f&_nc_ohc=DY2b9HbJCcgQ7kNvwFAPsuX&_nc_oc=AdmJ8w1FoPtNs3aYuzQK_C4jinHX2lVZSUwsOi9ll9bntxzjhHBUeFNUdnYzydk8HnvjZFQvekVeQVJi9ONJHWu0&_nc_zt=23&_nc_ht=scontent.fcdg4-1.fna&_nc_gid=XvN1_5XMQUlZxsa20agkHA&oh=00_Afa7AwyVbH7v-Cm1Kfb9qI_KnjjjIqQstPfGvCkKeceIrQ&oe=68C377ED",
        "title": "SALSA SUR LES QUAIS",
        "date": "MERCREDI - 20H À 23H",
        "type": "Soirée Latine 💃",
        "description": "Salsa sur les Quais s’installe le temps d’une soirée sous les Nefs. Un lieu unique, atypique voire magiiiiiiiiiiique ✨✨✨",
        "location": "📍 Machines de l'île de Nantes",
        "cost": "Événement Gratuit",
    }
    """
    with INPUT_FOLDER.joinpath("events.json").open("r", encoding="utf-8") as f:
        events = json.load(f)

    for i, event in enumerate(events):
        create_event_card(event, IMAGE_FOLDER.joinpath(f"output_event_card_{i}.jpg"))
