from pilmoji import Pilmoji
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from event_card_generator import EventCardGenerator

BASE_DIR = Path(__file__).parent
IMAGE_FOLDER = BASE_DIR.joinpath("images")
INPUT_FOLDER = BASE_DIR.joinpath("input")


class StoryEventCardGenerator(EventCardGenerator):
    """Story format event card generator (1080x1920) with gradient backgrounds and centered layout."""

    def __init__(self, width: int = 1080, height: int = 1920):
        """
        Initialize the story format event card generator.

        Args:
            width: Card width in pixels (default 1080)
            height: Card height in pixels (default 1920)
        """
        super().__init__(width, height)

        # Override settings for story format
        self.start_card = 20  # Start lower to accommodate banner

        # Design constants
        self.banner_height = 120

        # Gradient configuration - Change this value to control gradient area
        # 30% of card height (change to 1.0 for full card)
        self.gradient_height_ratio = 0.2

        # Spacing
        self.max_description_lines = 20

        # Data keys
        self._description_key = "description_long"

    def create_gradient_background(
        self,
        card: Image.Image,
        colors: tuple[tuple[int, int, int], tuple[int, int, int]],
    ):
        """
        Create a vertical gradient background for story format header.

        The gradient is limited to self.gradient_height_ratio of the card height.
        Set gradient_height_ratio to 1.0 for full card gradient.

        Args:
            card: PIL Image object to apply gradient to
            colors: Tuple of two RGB color tuples (top_color, bottom_color)
        """
        draw = ImageDraw.Draw(card)
        top_color, bottom_color = colors

        # Calculate gradient area height based on ratio
        gradient_height = int(self.card_height * self.gradient_height_ratio)

        for y in range(gradient_height):
            # Calculate blend ratio within the gradient area
            ratio = y / gradient_height

            # Interpolate between colors
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)

            draw.line([(0, y), (self.card_width, y)], fill=(r, g, b))

    def get_gradient_colors(
        self, date: str
    ) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        """
        Get gradient colors based on the day for story format.
        The gradient will blend from the day color to white (background color).

        Args:
            date: Date string containing day information

        Returns:
            Tuple of two RGB color tuples for gradient (top_color, white)
        """
        day = date.upper()

        # Monday/Lunes/Lundi - Orange/Yellow gradient
        if any(d in day for d in ["LUNES", "LUNDI", "MONDAY"]):
            return ((255, 193, 7), self.background_color)  # Orange to yellow
        # Tuesday/Martes/Mardi - Blue gradient
        elif any(d in day for d in ["MARTES", "MARDI", "TUESDAY"]):
            return ((63, 81, 181), self.background_color)  # Deep blue to light blue
        # Wednesday/Miércoles/Mercredi - Yellow gradient
        elif any(d in day for d in ["MIERCOLES", "MERCREDI", "WEDNESDAY"]):
            return ((255, 235, 59), self.background_color)  # Yellow to light yellow
        # Thursday/Jueves/Jeudi - Purple gradient
        elif any(d in day for d in ["JUEVES", "JEUDI", "THURSDAY"]):
            return ((156, 39, 176), self.background_color)  # Purple to light purple
        # Friday/Viernes/Vendredi - Red gradient
        elif any(d in day for d in ["VIERNES", "VENDREDI", "FRIDAY"]):
            return ((244, 67, 54), self.background_color)  # Red to light red
        # Saturday/Sábado/Samedi - Green gradient
        elif any(d in day for d in ["SABADO", "SAMEDI", "SATURDAY"]):
            return ((76, 175, 80), self.background_color)  # Green to light green
        # Sunday/Domingo/Dimanche - Green gradient (as shown in images)
        elif any(d in day for d in ["DOMINGO", "DIMANCHE", "SUNDAY"]):
            return ((76, 175, 80), self.background_color)  # Green to light green
        # Default - Orange gradient
        else:
            return ((255, 193, 7), self.background_color)

    def add_banner_text(self, card: Image.Image, date: str, banner_start_y: int):
        """
        Add centered date/time text to the story format banner.

        Args:
            card: PIL Image object representing the card
            date: Date string to display on banner
            banner_start_y: Y position where banner starts
        """
        draw = ImageDraw.Draw(card)
        font_banner = ImageFont.truetype(self.font_bold, self.banner_font_size)

        with Pilmoji(card) as pilmoji:
            bbox = draw.textbbox((0, 0), date, font=font_banner)
            text_width = bbox[2] - bbox[0]
            text_x = (self.card_width - text_width) // 2
            text_y = banner_start_y + (self.banner_height - self.banner_font_size) // 2
            pilmoji.text(
                (text_x, text_y), date, font=font_banner, fill=self.background_color
            )

    def create_event_card(self, event: dict[str, str], output_path: str):
        """
        Create a story format event card with gradient background and centered layout.

        Args:
            event: Dictionary containing event data
            output_path: Path where the generated card image should be saved
        """
        # Create base card with white background
        card = Image.new(
            "RGB", (self.card_width, self.card_height), self.background_color
        )

        # Create gradient background
        gradient_colors = self.get_gradient_colors(event["date"])
        self.create_gradient_background(card, gradient_colors)

        draw = ImageDraw.Draw(card)

        # Draw rectangular banner
        banner_color = self.get_color(event["date"])
        content_start_y = self.draw_banner(draw, self.start_card, banner_color)

        # Add banner text
        self.add_banner_text(card, event["date"], self.start_card)

        # Add story content
        # self.add_story_content(card, event, content_start_y)
        content_end_y = self.add_event_content(card, event, content_start_y)

        # Load and process event image (smaller for story format)
        self.max_crop_height = (self.card_height - 20) - (content_end_y + 20)
        img = self.load_and_process_image(event)
        img_x = (self.card_width - img.width) // 2
        card.paste(img, (img_x, content_end_y + 20))  # Start with some top margin

        # Save the card
        card.save(output_path, quality=95)
        print(f"✅ Saved story card at {output_path}")
