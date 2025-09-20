from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from event_card_generator import EventCardGenerator


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
        self.margin = 10
        self.left_margin = 150
        self.right_margin = 150

        # Text settings - adjusted to match images
        self.main_text_size = 90  # Smaller for better fit
        self.secondary_text_size = 40  # Smaller for better fit
        self.date_text_size = 50  # Smaller for better fit
        self.line_spacing = 100
        self.banner_font_size = 50

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

    def add_content(
        self, card: Image.Image, card_data: dict[str, str], content_start_y: int
    ) -> int:
        """Add all event content to the card."""
        y_pos = content_start_y + 150  # Small padding from banner

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

        # Add brand header
        y_pos = self.load_and_process_image(card, logo_path, self.start_card)

        draw = ImageDraw.Draw(card)

        # Draw inclined banner
        banner_start_y = y_pos + 100
        banner_color = self.get_color(card_data["day_name_fr"])
        content_start_y = self.draw_banner(draw, banner_start_y, banner_color)

        # Add banner text
        self.add_banner_text(
            card,
            f"{card_data['day_name_es']} / {card_data['day_name_fr']}",
            banner_start_y,
            ImageFont.truetype(self.font_bold, self.banner_font_size),
        )

        # # Add weather info if available
        # y_pos = self.start_card
        # if "weather" in card_data:
        #     weather_data = card_data["weather"]
        #     y_pos = self.add_event_info(
        #         card,
        #         f"{weather_data['emoji']} {weather_data['temperature']}°C - {weather_data['description']}",
        #         y_pos,
        #         ImageFont.truetype(self.font_regular, self.weather_text_size),
        #         section_spacing=100,
        #     )

        # y_pos = self.add_event_info(
        #     card,
        #     card_data["date"],
        #     y_pos,
        #     ImageFont.truetype(self.font_regular, self.date_text_size),
        # )

        # Add main message (centered in the middle area)
        self.add_content(card, card_data, content_start_y)

        # Save the card
        card.save(output_path, quality=95)
        print(f"✅ Saved motivation card at {output_path}")
