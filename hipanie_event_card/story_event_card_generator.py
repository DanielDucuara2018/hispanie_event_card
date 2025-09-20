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
        return (self.get_color(date), self.background_color)

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
        self.add_banner_text(
            card,
            event["date"],
            self.start_card,
            ImageFont.truetype(self.font_bold, self.banner_font_size),
        )

        # Add story content
        content_end_y = self.add_content(card, event, content_start_y)

        # Load and process event image (smaller for story format)
        self.max_crop_height = (self.card_height - 20) - (content_end_y + 20)
        img = self.load_and_process_image(event)
        img_x = (self.card_width - img.width) // 2
        card.paste(img, (img_x, content_end_y + 20))  # Start with some top margin

        # Save the card
        card.save(output_path, quality=95)
        print(f"✅ Saved story card at {output_path}")
