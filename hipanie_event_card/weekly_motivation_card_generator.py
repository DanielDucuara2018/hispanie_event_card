from pilmoji import Pilmoji
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from story_event_card_generator import StoryEventCardGenerator
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
IMAGE_FOLDER = BASE_DIR.joinpath("images")
INPUT_FOLDER = BASE_DIR.joinpath("input")


class WeeklyMotivationCardGenerator(StoryEventCardGenerator):
    """Weekly motivation card generator with gradient backgrounds and bilingual text."""

    def __init__(self, width: int = 1080, height: int = 1920):
        """
        Initialize the weekly motivation card generator.

        Args:
            width: Card width in pixels (default 1080)
            height: Card height in pixels (default 1920)
        """
        super().__init__(width, height)

        # Override settings for motivation cards
        self.start_card = 80  # Start higher for better date placement

        # Text settings - adjusted to match images
        self.main_text_size = 90  # Smaller for better fit
        self.secondary_text_size = 70  # Smaller for better fit
        self.date_text_size = 50  # Smaller for better fit
        self.brand_text_size = 100

        # Colors
        self.text_color = (0, 0, 0)  # Black text
        self.date_bg_color = (255, 255, 255, 230)  # More opaque white

    def add_date_section(self, card: Image.Image, card_data: dict):
        """
        Add date section with day number/month and bilingual day names in a centered rounded rectangle.

        Args:
            card: PIL Image object
            card_data: Dictionary with 'date', 'day_name_es', 'day_name_fr'
        """
        draw = ImageDraw.Draw(card)
        font_date = ImageFont.truetype(self.font_bold, self.date_text_size)

        # Calculate text dimensions for proper rectangle sizing
        date_text = card_data["date"]
        day_text = f"{card_data['day_name_es']} / {card_data['day_name_fr']}"

        date_bbox = draw.textbbox((0, 0), date_text, font=font_date)
        day_bbox = draw.textbbox((0, 0), day_text, font=font_date)

        # Use the wider text for rectangle width
        max_text_width = max(date_bbox[2] - date_bbox[0], day_bbox[2] - day_bbox[0])

        # Rectangle dimensions with padding
        padding = 40
        date_rect_width = max_text_width + (padding * 2)
        date_rect_height = 140
        date_rect_x = (self.card_width - date_rect_width) // 2
        date_rect_y = self.start_card

        # Draw rounded rectangle background
        self._draw_rounded_rectangle(
            draw,
            (
                date_rect_x,
                date_rect_y,
                date_rect_x + date_rect_width,
                date_rect_y + date_rect_height,
            ),
            self.date_bg_color,
            20,
        )

        # Center date text within rectangle
        date_text_x = (self.card_width - (date_bbox[2] - date_bbox[0])) // 2
        date_text_y = date_rect_y + 25
        draw.text(
            (date_text_x, date_text_y), date_text, font=font_date, fill=self.text_color
        )

        # Center day names text within rectangle
        day_text_x = (self.card_width - (day_bbox[2] - day_bbox[0])) // 2
        day_text_y = date_rect_y + 80
        draw.text(
            (day_text_x, day_text_y), day_text, font=font_date, fill=self.text_color
        )

    def add_main_message(self, card: Image.Image, card_data: dict, start_y: int):
        """
        Add main motivational message in both languages with proper centering and line wrapping.

        Args:
            card: PIL Image object
            card_data: Dictionary with 'spanish_text', 'french_text', 'emoji'
            start_y: Y position to start the message

        Returns:
            int: Y position after the message
        """
        draw = ImageDraw.Draw(card)
        margin = 80  # Side margins matching the images
        max_text_width = self.card_width - (2 * margin)

        with Pilmoji(card) as pilmoji:
            # Spanish text (larger, bold)
            font_main = ImageFont.truetype(self.font_bold, self.main_text_size)
            spanish_text = card_data["spanish_text"]
            if "emoji" in card_data:
                spanish_text += f" {card_data['emoji']}"

            # Wrap Spanish text
            wrapped_lines = self._wrap_text_custom(
                spanish_text, font_main, max_text_width, draw
            )
            current_y = start_y

            # Draw each line centered
            for line in wrapped_lines:
                bbox = draw.textbbox((0, 0), line, font=font_main)
                text_width = bbox[2] - bbox[0]
                text_x = (self.card_width - text_width) // 2
                pilmoji.text(
                    (text_x, current_y), line, font=font_main, fill=self.text_color
                )
                current_y += self.main_text_size + 10  # Tight line spacing

            current_y += 60  # Space between languages

            # French text (smaller, regular)
            font_secondary = ImageFont.truetype(
                self.font_regular, self.secondary_text_size
            )
            french_text = card_data["french_text"]
            if "emoji" in card_data:
                french_text += f" {card_data['emoji']}"

            # Wrap French text
            wrapped_lines = self._wrap_text_custom(
                french_text, font_secondary, max_text_width, draw
            )

            # Draw each line centered
            for line in wrapped_lines:
                bbox = draw.textbbox((0, 0), line, font=font_secondary)
                text_width = bbox[2] - bbox[0]
                text_x = (self.card_width - text_width) // 2
                pilmoji.text(
                    (text_x, current_y), line, font=font_secondary, fill=self.text_color
                )
                current_y += self.secondary_text_size + 8  # Tight line spacing

            return current_y

    def _wrap_text_custom(
        self, text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.Draw
    ) -> list[str]:
        """
        Custom text wrapping that handles emojis and provides better line breaks.

        Args:
            text: Text to wrap
            font: Font to use for measuring
            max_width: Maximum width in pixels
            draw: ImageDraw object for text measurement

        Returns:
            List of wrapped text lines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            # Test if adding this word would exceed max width
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_width:
                current_line.append(word)
            else:
                # Current line is full, start a new one
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, add it anyway
                    lines.append(word)

        # Add remaining words
        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def add_brand_footer(self, card: Image.Image, logo_path: str):
        """
        Add brand logo at the bottom of the card.

        Args:
            card: PIL Image object
            logo_path: Path to the logo image file
        """
        # Load logo
        logo = Image.open(logo_path)

        # Calculate logo size based on card width with margins
        margin = 100  # Margin from left and right sides
        max_logo_width = self.card_width - (2 * margin)

        # Calculate resize ratio to fit within card width
        width_ratio = max_logo_width / logo.width

        # Resize logo maintaining aspect ratio
        new_width = int(logo.width * width_ratio)
        new_height = int(logo.height * width_ratio)

        logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Position logo at bottom center
        logo_x = (self.card_width - new_width) // 2
        logo_y = self.card_height - new_height - 350  # 350px from bottom

        # Paste logo onto card
        if logo.mode == "RGBA":
            card.paste(logo, (logo_x, logo_y), logo)
        else:
            card.paste(logo, (logo_x, logo_y))

    def _draw_rounded_rectangle(self, draw, bbox, fill, radius):
        """Draw a rounded rectangle."""
        x1, y1, x2, y2 = bbox
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)

    def _wrap_text(
        self, text: str, font: ImageFont.ImageFont, max_width: int
    ) -> list[str]:
        """
        Wrap text to fit within max_width.

        Args:
            text: Text to wrap
            font: Font to use for measuring
            max_width: Maximum width in pixels

        Returns:
            List of wrapped text lines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]

            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def create_motivation_card(
        self, card_data: dict, output_path: Path, logo_path: Path
    ):
        """
        Create a weekly motivation card with proper text placement matching reference images.

        Args:
            card_data: Dictionary containing card data
            output_path: Path where to save the generated card
            logo_path: Path to the logo image file
        """
        # Create base card
        card = Image.new(
            "RGB", (self.card_width, self.card_height), self.background_color
        )

        # Create gradient background
        gradient_colors = self.get_gradient_colors(card_data["day_name_fr"])
        self.create_gradient_background(card, gradient_colors)

        # Add date section (at the top)
        self.add_date_section(card, card_data)

        # Add main message (centered in the middle area)
        message_start_y = 300  # Start after date section with good spacing
        self.add_main_message(card, card_data, message_start_y)

        # Add brand footer
        self.add_brand_footer(card, logo_path)

        # Save the card
        card.save(output_path, quality=95)
        print(f"✅ Saved motivation card at {output_path}")


# Example usage
if __name__ == "__main__":
    start_date = datetime.now()

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
            "french_text": "parce qu'aujourd'hui est un nouveau jour",
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

    # Example card data based on the images
    data_cards = [
        {
            "date": f"{single_date.day} {FR_MONTHS[single_date.strftime('%B')].upper()}",
            "day_name_es": ES_DAYS[single_date.strftime("%A")],
            "day_name_fr": FR_DAYS[single_date.strftime("%A")],
            **WEEKLY_MESSAGES[single_date.strftime("%A")],
        }
        for single_date in (start_date + timedelta(n) for n in range(7))
    ]

    generator = WeeklyMotivationCardGenerator()
    for city in ["paris", "nantes"]:
        for card_data in data_cards:
            output_path = IMAGE_FOLDER.joinpath(
                f"motivation_card_{city}_{card_data['date']}.png"
            )
            generator.create_motivation_card(
                card_data, output_path, INPUT_FOLDER.joinpath(f"{city}_logo.png")
            )
