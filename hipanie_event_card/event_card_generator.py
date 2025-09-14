import requests
from pilmoji import Pilmoji
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class EventCardGenerator:
    """Event card generator with customizable design settings."""

    def __init__(self, width: int = 1080, height: int = 1350):
        """
        Initialize the event card generator.

        Args:
            width: Card width in pixels
            height: Card height in pixels
        """
        self.card_width = width
        self.card_height = height

        # Design constants
        self.max_crop_height = 600
        self.banner_height = 90
        self.margin = 40
        self.angle_offset = 20
        self.left_margin = 40
        self.right_margin = 40

        # Font settings
        self.font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        self.font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

        # Font sizes
        self.banner_font_size = 42
        self.type_font_size = 33
        self.title_font_size = 35
        self.desc_font_size = 30
        self.cost_font_size = 30
        self.location_font_size = 30

        # Spacing
        self.line_spacing = 45
        self.section_spacing = 80
        self.max_description_lines = 3

        # Data keys
        self._description_key = "description_short"

    def load_and_process_image(self, event: dict[str, str]) -> Image.Image:
        """
        Load image from URL or file path and crop to show top 3/4 of the image only if height > width.

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

        img_width, img_height = img.size

        # Only crop to max height if image exceeds threshold
        if img_height > self.max_crop_height:
            cropped_height = self.max_crop_height
            # If image is wider than card, also crop horizontally
            if img_width > self.card_width:
                crop_x = (img_width - self.card_width) // 2
                img = img.crop((crop_x, 0, crop_x + self.card_width, cropped_height))
            else:
                img = img.crop((0, 0, img_width, cropped_height))
        else:
            # Keep original size, only crop horizontally if wider than card
            if img_width > self.card_width:
                crop_x = (img_width - self.card_width) // 2
                img = img.crop((crop_x, 0, crop_x + self.card_width, img_height))

        return img

    def get_banner_color(self, date: str) -> tuple[int, int, int]:
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

    def draw_banner(
        self,
        draw: ImageDraw.Draw,
        banner_start_y: int,
        banner_color: tuple[int, int, int],
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
        # Draw inclined rectangle as polygon
        banner_points = [
            (self.margin, banner_start_y + self.angle_offset),  # top-left (lower)
            (self.card_width - self.margin, banner_start_y),  # top-right (higher)
            (
                self.card_width - self.margin,
                banner_start_y + self.banner_height,
            ),  # bottom-right
            (
                self.margin,
                banner_start_y + self.banner_height + self.angle_offset,
            ),  # bottom-left (lower)
        ]

        draw.polygon(banner_points, fill=banner_color)
        return banner_start_y + self.banner_height + self.angle_offset + 30

    def add_banner_text(self, card: Image.Image, date: str, banner_start_y: int):
        """
        Add centered date/time text to the banner.

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
            text_y = (
                banner_start_y
                + (self.banner_height - self.banner_font_size) // 2
                + self.angle_offset // 2
            )
            pilmoji.text((text_x, text_y), date, font=font_banner, fill="white")

    def _wrap_paragraph(
        self,
        paragraph: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
        draw: ImageDraw.Draw,
    ) -> list[str]:
        """
        Wrap a single paragraph to fit within specified width.

        Args:
            paragraph: Single paragraph text to wrap
            font: Font to use for text measurement
            max_width: Maximum width in pixels
            draw: ImageDraw object for text measurement

        Returns:
            List of wrapped lines for the paragraph
        """
        lines = []
        words = paragraph.split()
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

        return lines

    def _wrap_text_with_newlines(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
        draw: ImageDraw.Draw,
    ) -> list[str]:
        """
        Wrap text that contains explicit newlines.

        Args:
            text: Text containing newlines to wrap
            font: Font to use for text measurement
            max_width: Maximum width in pixels
            draw: ImageDraw object for text measurement

        Returns:
            List of wrapped lines preserving paragraph structure
        """
        lines = []
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            if not paragraph.strip():  # Empty line
                lines.append("")
                continue

            paragraph_lines = self._wrap_paragraph(paragraph, font, max_width, draw)
            lines.extend(paragraph_lines)

        return lines

    def wrap_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
        draw: ImageDraw.Draw,
    ) -> list[str]:
        """
        Wrap text to fit within specified width, limiting to max lines.
        Handles explicit newlines (\n) if present, otherwise splits by words.

        Args:
            text: Text to wrap
            font: Font to use for text measurement
            max_width: Maximum width in pixels
            draw: ImageDraw object for text measurement

        Returns:
            List of text lines that fit within the width
        """
        # Check if text contains explicit newlines
        if "\n" in text:
            lines = self._wrap_text_with_newlines(text, font, max_width, draw)
        else:
            lines = self._wrap_paragraph(text, font, max_width, draw)

        return lines[: self.max_description_lines]

    def add_event_type(
        self, card: Image.Image, event: dict[str, str], y_position: int
    ) -> int:
        """Add event type/category with emoji to the card."""
        font_type = ImageFont.truetype(self.font_regular, self.type_font_size)
        with Pilmoji(card) as pilmoji:
            pilmoji.text(
                (self.left_margin, y_position),
                f"🎉 {event['type']}",
                font=font_type,
                fill="black",
            )
        return y_position + self.section_spacing

    def add_event_title(
        self, card: Image.Image, event: dict[str, str], y_position: int
    ) -> int:
        """Add event title to the card."""
        font_title = ImageFont.truetype(self.font_bold, self.title_font_size)
        with Pilmoji(card) as pilmoji:
            pilmoji.text(
                (self.left_margin, y_position),
                event["title"],
                font=font_title,
                fill="black",
            )
        return y_position + self.section_spacing

    def add_event_description(
        self, card: Image.Image, event: dict[str, str], y_position: int
    ) -> int:
        """Add wrapped event description to the card."""
        draw = ImageDraw.Draw(card)
        font_desc = ImageFont.truetype(self.font_regular, self.desc_font_size)
        max_desc_width = self.card_width - self.left_margin - self.right_margin

        lines = self.wrap_text(
            event[self._description_key], font_desc, max_desc_width, draw
        )

        with Pilmoji(card) as pilmoji:
            for i, line in enumerate(lines):
                pilmoji.text(
                    (self.left_margin, y_position + i * self.line_spacing),
                    line,
                    font=font_desc,
                    fill="black",
                )

        return y_position + len(lines) * self.line_spacing + self.section_spacing

    def add_event_cost(
        self, card: Image.Image, event: dict[str, str], y_position: int
    ) -> int:
        """Add event cost/pricing information to the card."""
        font_cost = ImageFont.truetype(self.font_bold, self.cost_font_size)
        with Pilmoji(card) as pilmoji:
            pilmoji.text(
                (self.left_margin, y_position),
                f"🎫 {event['cost']}",
                font=font_cost,
                fill="black",
            )
        return y_position + 50

    def add_separator_line(self, card: Image.Image, y_position: int) -> int:
        """Add a horizontal separator line to the card."""
        draw = ImageDraw.Draw(card)
        draw.line(
            [
                (self.left_margin, y_position),
                (self.card_width - self.right_margin, y_position),
            ],
            fill="black",
            width=2,
        )
        return y_position + 30

    def add_event_location(
        self, card: Image.Image, event: dict[str, str], y_position: int
    ) -> int:
        """Add event location to the card."""
        font_location = ImageFont.truetype(self.font_regular, self.location_font_size)
        with Pilmoji(card) as pilmoji:
            pilmoji.text(
                (self.left_margin, y_position),
                f"📍 {event['location']}",
                font=font_location,
                fill="black",
            )
        return y_position + 50

    def add_event_content(
        self, card: Image.Image, event: dict[str, str], content_start_y: int
    ) -> int:
        """Add all event content to the card."""
        y_pos = content_start_y + 20  # Small padding from banner

        y_pos = self.add_event_type(card, event, y_pos)
        y_pos = self.add_event_title(card, event, y_pos)
        y_pos = self.add_event_description(card, event, y_pos)
        y_pos = self.add_event_cost(card, event, y_pos)
        y_pos = self.add_separator_line(card, y_pos)
        y_pos = self.add_event_location(card, event, y_pos)

        return y_pos

    def create_event_card(self, event: dict[str, str], output_path: str):
        """
        Create an event card with standardized design.

        Args:
            event: Dictionary containing event data
            output_path: Path where the generated card image should be saved
        """
        # Create base card
        card = Image.new("RGB", (self.card_width, self.card_height), "white")
        draw = ImageDraw.Draw(card)

        # Load and process event image
        img = self.load_and_process_image(event)
        img_x = (self.card_width - img.width) // 2
        card.paste(img, (img_x, 0))

        # Draw inclined banner
        banner_start_y = img.height
        banner_color = self.get_banner_color(event["date"])
        content_start_y = self.draw_banner(draw, banner_start_y, banner_color)

        # Add banner text
        self.add_banner_text(card, event["date"], banner_start_y)

        # Add event content
        self.add_event_content(card, event, content_start_y)

        # Save the card
        card.save(output_path, quality=95)
        print(f"✅ Saved card at {output_path}")
