# import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path

BASE_DIR = Path(__file__).parent
IMAGE_FOLDER = BASE_DIR.joinpath("images")

# 🔹 Card size (based on your samples, WhatsApp shared images ~1080x1350)
CARD_WIDTH, CARD_HEIGHT = 1080, 1350

# 🔹 Fonts (adjust paths depending on your system)
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
    img = img.resize((CARD_WIDTH, int(CARD_HEIGHT * 0.45)))
    card.paste(img, (0, 0))

    # --- Blue/Green banner with date ---
    banner_h = 80
    banner_color = (0, 180, 255) if "VENDREDI" in event["date"] else (100, 255, 100)
    draw.rectangle([0, int(CARD_HEIGHT * 0.45), CARD_WIDTH, int(CARD_HEIGHT * 0.45) + banner_h], fill=banner_color)

    font_banner = ImageFont.truetype(FONT_BOLD, 50)
    bbox = draw.textbbox((0, 0), event["date"], font=font_banner)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((CARD_WIDTH - w) // 2, int(CARD_HEIGHT * 0.45) + (banner_h - h) // 2),
              event["date"], font=font_banner, fill="black")

    # --- Subtitle ---
    font_sub = ImageFont.truetype(FONT_BOLD, 45)
    draw.text((50, int(CARD_HEIGHT * 0.45) + banner_h + 40),
              event["subtitle"], font=font_sub, fill="black")

    # --- Title ---
    font_title = ImageFont.truetype(FONT_BOLD, 60)
    draw.text((50, int(CARD_HEIGHT * 0.45) + banner_h + 120),
              event["title"], font=font_title, fill="black")

    # --- Description ---
    font_desc = ImageFont.truetype(FONT_REGULAR, 38)
    desc_y = int(CARD_HEIGHT * 0.45) + banner_h + 220
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

    for l in lines:
        draw.text((50, desc_y), l.strip(), font=font_desc, fill="black")
        desc_y += 50

    # --- Free Event indicator ---
    font_free = ImageFont.truetype(FONT_REGULAR, 40)
    draw.text((50, desc_y + 30), "📅 Événement Gratuit", font=font_free, fill="black")

    # --- Location ---
    font_loc = ImageFont.truetype(FONT_REGULAR, 40)
    draw.text((50, desc_y + 100), event["location"], font=font_loc, fill="black")

    # --- Save output ---
    card.save(output_path, quality=95)
    print(f"✅ Saved card at {output_path}")


if __name__ == "__main__":
    # Example JSON input
    event_json = {
        "image": "https://scontent.fcdg4-1.fna.fbcdn.net/v/t39.30808-6/520225612_1287586610043747_9068125171068301630_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=75d36f&_nc_ohc=DY2b9HbJCcgQ7kNvwFAPsuX&_nc_oc=AdmJ8w1FoPtNs3aYuzQK_C4jinHX2lVZSUwsOi9ll9bntxzjhHBUeFNUdnYzydk8HnvjZFQvekVeQVJi9ONJHWu0&_nc_zt=23&_nc_ht=scontent.fcdg4-1.fna&_nc_gid=XvN1_5XMQUlZxsa20agkHA&oh=00_Afa7AwyVbH7v-Cm1Kfb9qI_KnjjjIqQstPfGvCkKeceIrQ&oe=68C377ED",
        "title": "SALSA SUR LES QUAIS",
        "date": "MERCREDI - 20H À 23H",
        "subtitle": "Soirée Latine 💃",
        "description": "Salsa sur les Quais s’installe le temps d’une soirée sous les Nefs. Un lieu unique, atypique voire magiiiiiiiiiiique ✨✨✨",
        "location": "📍 Machines de l'île de Nantes"
    }
    # event = json.loads(event_json)
    create_event_card(event_json, IMAGE_FOLDER.joinpath("output_event_card.jpg"))
