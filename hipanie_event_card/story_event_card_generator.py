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

        # Design constants
        self.max_crop_height = 400  # Smaller image for story format
        self.banner_height = 120

        # Spacing
        self.max_description_lines = 10

        # Data keys
        self._description_key = "description_long"

    def create_gradient_background(
        self,
        card: Image.Image,
        colors: tuple[tuple[int, int, int], tuple[int, int, int]],
    ):
        """
        Create a vertical gradient background for story format.

        Args:
            card: PIL Image object to apply gradient to
            colors: Tuple of two RGB color tuples (top_color, bottom_color)
        """
        draw = ImageDraw.Draw(card)
        top_color, bottom_color = colors

        y_height = self.card_height / 2
        for y in range(int(y_height)):
            # Calculate blend ratio
            ratio = y / y_height

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

        Args:
            date: Date string containing day information

        Returns:
            Tuple of two RGB color tuples for gradient
        """
        day = date.upper()
        if "VENDREDI" in day or "VIERNES" in day or "FRIDAY" in day:
            return ((67, 160, 71), (200, 255, 200))  # Green gradient
        elif "JEUDI" in day or "JUEVES" in day or "THURSDAY" in day:
            return ((66, 165, 245), (200, 230, 255))  # Blue gradient
        elif "MERCREDI" in day or "MIERCOLES" in day or "WEDNESDAY" in day:
            return ((102, 187, 106), (220, 255, 220))  # Light green gradient
        elif "SABADO" in day or "SAMEDI" in day or "SATURDAY" in day:
            return ((255, 87, 87), (255, 200, 200))  # Red gradient
        else:
            return ((255, 193, 7), (255, 240, 200))  # Yellow/orange gradient

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
            pilmoji.text((text_x, text_y), date, font=font_banner, fill="white")

    def create_event_card(self, event: dict[str, str], output_path: str):
        """
        Create a story format event card with gradient background and centered layout.

        Args:
            event: Dictionary containing event data
            output_path: Path where the generated card image should be saved
        """
        # Create base card with white background
        card = Image.new("RGB", (self.card_width, self.card_height), "white")

        # Create gradient background
        gradient_colors = self.get_gradient_colors(event["date"])
        self.create_gradient_background(card, gradient_colors)

        draw = ImageDraw.Draw(card)

        # Draw rectangular banner
        banner_start_y = 50
        banner_color = self.get_banner_color(event["date"])
        content_start_y = self.draw_banner(draw, banner_start_y, banner_color)

        # Add banner text
        self.add_banner_text(card, event["date"], banner_start_y)

        # Add story content
        # self.add_story_content(card, event, content_start_y)
        self.add_event_content(card, event, content_start_y)

        # Load and process event image (smaller for story format)
        # img = self.load_and_process_image(event)
        # img_x = (self.card_width - img.width) // 2
        # card.paste(img, (img_x, content_end_y))  # Start with some top margin

        # Save the card
        card.save(output_path, quality=95)
        print(f"✅ Saved story card at {output_path}")
