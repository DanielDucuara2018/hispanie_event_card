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


def create_event_card(event: dict[str, str], output_path: str):
    """
    Create an event card with given info.
    """
    # --- Base card ---
    card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "white")
    draw = ImageDraw.Draw(card)

    # --- Event image (top half) ---
    if event["image"].startswith("http"):
        response = requests.get(event["image"])
        img = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        img = Image.open(event["image"]).convert("RGB")

    # Resize image proportionally to fit the top half of the card
    img_width, img_height = img.size
    max_width, max_height = CARD_WIDTH, int(CARD_HEIGHT * 0.45)
    aspect_ratio = img_width / img_height

    if img_width > max_width or img_height > max_height:
        if img_width / max_width > img_height / max_height:
            new_width = max_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center the image horizontally
    img_x = (CARD_WIDTH - img.width) // 2
    card.paste(img, (img_x, 0))

    # --- Blue/Green banner with date ---
    banner_h = 80
    banner_color = (
        (0, 180, 255) if "VENDREDI" in event["date"].upper() else (100, 255, 100)
    )
    draw.rectangle(
        [0, int(CARD_HEIGHT * 0.45), CARD_WIDTH, int(CARD_HEIGHT * 0.45) + banner_h],
        fill=banner_color,
    )

    font_banner = ImageFont.truetype(FONT_BOLD, 50)
    with Pilmoji(card) as pilmoji:
        bbox = draw.textbbox((0, 0), event["date"], font=font_banner)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pilmoji.text(
            ((CARD_WIDTH - w) // 2, int(CARD_HEIGHT * 0.45) + (banner_h - h) // 2),
            event["date"],
            font=font_banner,
            fill="black",
        )

    # --- Type ---
    font_sub = ImageFont.truetype(FONT_BOLD, 35)
    with Pilmoji(card) as pilmoji:
        pilmoji.text(
            (50, int(CARD_HEIGHT * 0.45) + banner_h + 40),
            event["type"],
            font=font_sub,
            fill="black",
        )

    # --- Title ---
    font_title = ImageFont.truetype(FONT_BOLD, 45)
    with Pilmoji(card) as pilmoji:
        pilmoji.text(
            (50, int(CARD_HEIGHT * 0.45) + banner_h + 120),
            event["title"],
            font=font_title,
            fill="black",
        )

    # --- Description ---
    font_desc = ImageFont.truetype(FONT_REGULAR, 30)
    desc_y = int(CARD_HEIGHT * 0.45) + banner_h + 240
    max_width = CARD_WIDTH - 100
    desc_text = event["description"]

    # Wrap description text
    lines = []
    words = desc_text.split()
    line = ""
    for word in words:
        test_line = line + " " + word
        bbox = draw.textbbox((0, 0), test_line, font=font_desc)
        if bbox[2] - bbox[0] <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    lines.append(line)

    with Pilmoji(card) as pilmoji:
        for line in lines:
            pilmoji.text((50, desc_y), line.strip(), font=font_desc, fill="black")
            desc_y += 40

    # --- Free Event indicator ---
    font_free = ImageFont.truetype(FONT_REGULAR, 40)
    with Pilmoji(card) as pilmoji:
        pilmoji.text(
            (50, desc_y + 70), f"📅 {event['cost']}", font=font_free, fill="black"
        )

    # --- Location ---
    font_loc = ImageFont.truetype(FONT_REGULAR, 40)
    with Pilmoji(card) as pilmoji:
        pilmoji.text((50, desc_y + 140), event["location"], font=font_loc, fill="black")

    # --- Save output ---
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
