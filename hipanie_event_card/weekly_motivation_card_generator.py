from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from story_event_card_generator import StoryEventCardGenerator

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


class WeeklyMotivationCardGenerator(StoryEventCardGenerator):
    """Weekly motivation card generator with gradient backgrounds and bilingual text."""

    def __init__(self, width, height):
        """
        Initialize the weekly motivation card generator.

        Args:
            width: Card width in pixels (default 1080)
            height: Card height in pixels (default 1920)
        """
        super().__init__(width, height)

        # Override settings for motivation cards
        self.start_card = 300  # Start higher for better date placement
        self.margin = 80
        self.left_margin = 80
        self.right_margin = 80

        # Text settings - adjusted to match images
        self.main_text_size = 90  # Smaller for better fit
        self.secondary_text_size = 70  # Smaller for better fit
        self.date_text_size = 50  # Smaller for better fit
        self.line_spacing = 100
        self.banner_font_size = 50

        # Colors
        self.text_color = (0, 0, 0)  # Black text
        self.date_bg_color = (255, 255, 255, 230)  # More opaque white

        # Banner settings
        self.banner_text_color = "black"  # Default banner color (white)
        self.banner_width_ratio = 0.8  # Full width by default
        self.banner_text_position_ratio = (
            0.4  # Center position by default (0.0 = left, 1.0 = right)
        )
        self.banner_angle_offset = 20
        self.banner_height = 90
        self.banner_angle_offset = 0

        # Weather settings
        self.weather_text_size = 40
        self.weather_margin_top = 50

    def add_content(
        self, card: Image.Image, card_data: dict[str, str], content_start_y: int
    ) -> int:
        """Add all event content to the card."""
        y_pos = content_start_y + 200  # Small padding from banner

        y_pos = self.add_event_info(
            card,
            f"{card_data['spanish_text']} {card_data['emoji']}",
            y_pos,
            ImageFont.truetype(self.font_bold, self.main_text_size),
            section_spacing=2000,
            split_text=True,
        )
        y_pos = self.add_event_info(
            card,
            f"{card_data['french_text']} {card_data['emoji']}",
            y_pos,
            ImageFont.truetype(self.font_regular, self.secondary_text_size),
            section_spacing=500,
            split_text=True,
        )

        return y_pos

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

        # Add weather info if available
        y_pos = self.start_card
        if "weather" in card_data:
            weather_data = card_data["weather"]
            y_pos = self.add_event_info(
                card,
                f"{weather_data['emoji']} {weather_data['temperature']}°C - {weather_data['description']}",
                y_pos,
                ImageFont.truetype(self.font_regular, self.weather_text_size),
                section_spacing=100,
            )

        y_pos = self.add_event_info(
            card,
            card_data["date"],
            y_pos,
            ImageFont.truetype(self.font_regular, self.date_text_size),
        )

        draw = ImageDraw.Draw(card)

        # Draw inclined banner
        banner_start_y = y_pos
        banner_color = self.get_color(card_data["day_name_fr"])
        content_start_y = self.draw_banner(draw, banner_start_y, banner_color)
        # Add banner text
        self.add_banner_text(
            card,
            f"{card_data['day_name_es']} / {card_data['day_name_fr']} >",
            banner_start_y,
            ImageFont.truetype(self.font_bold, self.banner_font_size),
        )

        # Add main message (centered in the middle area)
        self.add_content(card, card_data, content_start_y)

        # Add brand footer
        self.add_brand_footer(card, logo_path)

        # Save the card
        card.save(output_path, quality=95)
        print(f"✅ Saved motivation card at {output_path}")
