import logging
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from event_card_generator import EventCardGenerator

logger = logging.getLogger(__name__)


class MotivationCardGenerator(EventCardGenerator):
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
        self.start_card = 50  # Start higher for better date placement
        self.margin = 0
        self.left_margin = 150
        self.right_margin = 150

        # Image settings
        self.image_resize_ratio = 0.5  # Resize images to 70% of available width

        # Text settings - adjusted to match images
        self.main_text_size = 90  # Smaller for better fit
        self.secondary_text_size = 40  # Smaller for better fit
        self.date_text_size = 50  # Smaller for better fit
        self.line_spacing = 100
        self.banner_font_size = 60

        # Colors
        self.text_color = (0, 0, 0)  # Black text
        self.date_bg_color = (255, 255, 255, 230)  # More opaque white

        # Banner settings
        self.banner_text_color = "black"  # Default banner color (white)
        self.banner_width_ratio = 1  # Full width by default
        self.banner_text_position_ratio = (
            0.5  # Center position by default (0.0 = left, 1.0 = right)
        )
        self.banner_height = 150
        self.banner_angle_offset = 0

        # Weather settings
        self.weather_text_size = 40
        self.weather_margin_top = 50

    def add_header(
        self, card: Image.Image, text_date: str, logo_path: Path, logo_x: int = 75
    ) -> int:
        """
        Add a header with the logo at the top of the card.

        Args:
            card: PIL Image object
            logo_path: Path to the logo image file

        Returns:
            Height of the logo image after placement
        """
        # Add brand header and get logo position info
        logo_height = self.load_and_process_image(
            card, logo_path, self.start_card, content_start_x=logo_x, resize=True
        )

        # Add vertical line and date text next to logo
        logo_img = Image.open(logo_path)
        logo_width = int(logo_img.width * self.image_resize_ratio)

        # Add vertical line
        self.add_vertical_line(
            card, self.start_card, logo_width, logo_x / 2, logo_height
        )

        # Add date text
        self.add_date_text(card, text_date, self.start_card, logo_width, logo_x / 2)

        return logo_height

    def add_vertical_line(
        self,
        card: Image.Image,
        logo_y: int,
        logo_width: int,
        logo_x: int,
        logo_height: int,
    ):
        """
        Add a vertical line to the right of the logo.

        Args:
            card: PIL Image object
            logo_y: Y position of the logo
            logo_width: Width of the logo
            logo_x: X position of the logo
            logo_height: Height of the logo
        """
        draw = ImageDraw.Draw(card)

        # Position vertical line between logo and date
        line_x = logo_x + logo_width + 100
        line_y1 = logo_y
        line_y2 = logo_y + logo_height

        # Draw vertical line
        draw.line([(line_x, line_y1), (line_x, line_y2)], fill=(0, 0, 0), width=3)

    def add_date_text(
        self,
        card: Image.Image,
        date_text: str,
        logo_y: int,
        logo_width: int,
        logo_x: int,
    ):
        """
        Add date text to the right of the vertical line.

        Args:
            card: PIL Image object
            date_text: Date text to display
            logo_y: Y position of the logo
            logo_width: Width of the logo
            logo_x: X position of the logo
        """
        # Position date to the right of the line
        date_x = logo_x + logo_width + 200  # 100 for line + 100 for spacing
        date_y = logo_y - 20  # Center vertically with logo

        self.add_event_info(
            card,
            date_text,
            date_y,
            ImageFont.truetype(self.font_regular, self.date_text_size),
            x_position=date_x,
        )

    def add_banner(
        self, card: Image.Image, card_data: dict[str, str], content_start_y: int
    ) -> int:
        """
        Add a banner below the header with day names.

        Args:
            card: PIL Image object
            card_data: Dictionary containing card data

        Returns:
            Y position after the banner
        """
        draw = ImageDraw.Draw(card)
        # Draw banner
        banner_start_y = content_start_y + 100
        banner_color = self.get_color(card_data["day_name_fr"])
        content_start_y = self.draw_banner(draw, banner_start_y, banner_color)
        # Add banner text
        self.add_banner_text(
            card,
            f"{card_data['day_name_es']} / {card_data['day_name_fr']}",
            banner_start_y,
            ImageFont.truetype(self.font_bold, self.banner_font_size),
        )
        return content_start_y

    def draw_rounded_rectangle_banner(
        self,
        card: Image.Image,
        text: str,
        y_position: int,
        font_type: ImageFont.FreeTypeFont,
    ) -> int:
        """
        Draw a rounded rectangle banner with black border and card background color.

        Args:
            card: PIL Image object
            text: Text to display in the rectangle
            y_position: Y position for the rectangle
            font_type: Font to use for the text

        Returns:
            Y position after the rectangle banner
        """
        draw = ImageDraw.Draw(card)

        # Calculate text dimensions
        bbox = draw.textbbox((0, 0), text, font=font_type)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Rectangle dimensions with padding
        padding_x = 40
        padding_y = 20
        rect_width = text_width + (padding_x * 2)
        rect_height = text_height + (padding_y * 2)
        radius = 25  # Rounded corner radius

        # Center the rectangle horizontally
        rect_x = (self.card_width - rect_width) // 2
        rect_y = y_position

        # Draw border
        self._draw_rounded_rectangle(
            draw,
            (rect_x, rect_y, rect_x + rect_width, rect_y + rect_height),
            (0, 0, 0),
            radius,
            width=3,
        )

        # Center text in rectangle
        text_x = rect_x + (rect_width - text_width) // 2
        text_y = rect_y + (rect_height - text_height) // 2

        y_pos = self.add_event_info(card, text, text_y, font_type, x_position=text_x)

        return y_pos

    def _draw_rounded_rectangle(self, draw, bbox, outline, radius, width=1):
        """Draw a rounded rectangle border."""
        x1, y1, x2, y2 = bbox

        # Draw border lines
        draw.line(
            [(x1 + radius, y1), (x2 - radius, y1)], fill=outline, width=width
        )  # Top
        draw.line(
            [(x1 + radius, y2), (x2 - radius, y2)], fill=outline, width=width
        )  # Bottom
        draw.line(
            [(x1, y1 + radius), (x1, y2 - radius)], fill=outline, width=width
        )  # Left
        draw.line(
            [(x2, y1 + radius), (x2, y2 - radius)], fill=outline, width=width
        )  # Right

        # Draw corner arcs
        draw.arc(
            [x1, y1, x1 + radius * 2, y1 + radius * 2],
            180,
            270,
            fill=outline,
            width=width,
        )
        draw.arc(
            [x2 - radius * 2, y1, x2, y1 + radius * 2],
            270,
            360,
            fill=outline,
            width=width,
        )
        draw.arc(
            [x1, y2 - radius * 2, x1 + radius * 2, y2],
            90,
            180,
            fill=outline,
            width=width,
        )
        draw.arc(
            [x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=width
        )

    def add_content(
        self, card: Image.Image, card_data: dict[str, str], content_start_y: int
    ) -> int:
        """Add all event content to the card."""
        y_pos = content_start_y + 150  # Small padding from banner

        # Add Spanish text (main message)
        y_pos = self.add_event_info(
            card,
            f"{card_data['spanish_text']} {card_data['emoji']}",
            y_pos,
            ImageFont.truetype(self.font_bold, self.main_text_size),
            section_spacing=100,
            split_text=True,
        )

        # Add French text in rounded rectangle banner
        y_pos = self.draw_rounded_rectangle_banner(
            card,
            f"{card_data['french_text']} {card_data['emoji']}",
            y_pos,
            ImageFont.truetype(self.font_regular, self.secondary_text_size),
        )

        return y_pos

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
        # Add header
        logo_height = self.add_header(card, card_data["date"], logo_path)

        # Add banner
        content_start_y = self.add_banner(card, card_data, logo_height)

        # Add main message (centered in the middle area)
        self.add_content(card, card_data, content_start_y)

        # Save the card
        card.save(output_path, quality=95)
        logger.info(f"✅ Saved motivation card at {output_path}")
