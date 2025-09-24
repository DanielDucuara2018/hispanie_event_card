import requests
from pilmoji import Pilmoji
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path


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
        self.start_card = 0
        self.background_color = (255, 255, 255)  # White
        self.margin = 40
        self.left_margin = 40
        self.right_margin = 40

        # Banner settings
        self.banner_text_color = (255, 255, 255)  # Default banner color (white)
        self.banner_width_ratio = 1.0  # Full width by default
        self.banner_text_position_ratio = (
            0.5  # Center position by default (0.0 = left, 1.0 = right)
        )
        self.banner_angle_offset = 20
        self.banner_height = 90

        # Image constants
        self.max_crop_height = 675
        self.image_resize_ratio = 1.0  # No resize by default

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
        self.line_spacing = 40
        self.section_spacing = 80
        self.max_description_lines = 4

        # Data keys
        self._description_key = "description_short"

    def load_and_process_image(
        self,
        card: Image.Image,
        image_path: str | Path,
        content_start_y: int,
        *,
        content_start_x: int | None = None,
        resize: bool = False,
    ) -> int:
        """
        Load image from URL or file path and process it to fit the card with proper margins.

        Args:
            event: Dictionary containing event data with 'image' key

        Returns:
            PIL Image object processed and ready for card
        """
        image_path = str(image_path)
        if image_path.startswith("http"):
            response = requests.get(image_path)
            img = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            img = Image.open(image_path)

        img_width, img_height = img.size

        # Calculate available width (card width minus margins)
        available_width = self.card_width - (2 * self.margin)

        # Resize image if it's wider than available width
        if img_width > available_width or resize:
            # Calculate resize ratio to fit within available width
            resize_ratio = available_width / img_width
            if resize:
                resize_ratio = self.image_resize_ratio
            new_width = int(img_width * resize_ratio)
            new_height = int(img_height * resize_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img_width, img_height = new_width, new_height

        # Crop height if image is too tall
        if img_height > self.max_crop_height:
            img = img.crop((0, 0, img_width, self.max_crop_height))

        img_x = (self.card_width - img.width) // 2
        if content_start_x is not None:
            img_x = content_start_x

        if img.mode == "RGBA":
            card.paste(img, (img_x, content_start_y), img)
        else:
            card.paste(img, (img_x, content_start_y))

        return img.height

    def get_color(self, date: str) -> tuple[int, int, int]:
        """
        Determine banner color based on the day of the week in the date string.

        Args:
            date: Date string containing day information

        Returns:
            RGB color tuple for the banner
        """
        day = date.upper()

        # Monday/Lunes/Lundi - Orange
        if any(d in day for d in ["LUNES", "LUNDI", "MONDAY"]):
            return (255, 152, 0)  # Orange
        # Tuesday/Martes/Mardi - Blue
        elif any(d in day for d in ["MARTES", "MARDI", "TUESDAY"]):
            return (33, 150, 243)  # Blue
        # Wednesday/Miércoles/Mercredi - Yellow
        elif any(d in day for d in ["MIERCOLES", "MERCREDI", "WEDNESDAY"]):
            return (204, 153, 0)  # Yellow
        # Thursday/Jueves/Jeudi - Purple
        elif any(d in day for d in ["JUEVES", "JEUDI", "THURSDAY"]):
            return (156, 39, 176)  # Purple
        # Friday/Viernes/Vendredi - Red
        elif any(d in day for d in ["VIERNES", "VENDREDI", "FRIDAY"]):
            return (244, 67, 54)  # Red
        # Saturday/Sábado/Samedi - Green
        elif any(d in day for d in ["SABADO", "SAMEDI", "SATURDAY"]):
            return (76, 175, 80)  # Green
        # Sunday/Domingo/Dimanche - Teal
        elif any(d in day for d in ["DOMINGO", "DIMANCHE", "SUNDAY"]):
            return (0, 150, 136)  # Teal
        # Default - Orange
        else:
            return (255, 152, 0)  # Orange

    def draw_banner(
        self,
        draw: ImageDraw.Draw,
        banner_start_y: int,
        banner_color: tuple[int, int, int],
    ) -> int:
        """
        Draw an inclined banner rectangle on the card with adjustable width.

        Args:
            draw: ImageDraw object for drawing on the card
            banner_start_y: Y position where banner starts
            banner_color: RGB color tuple for the banner
            banner_width_ratio: Ratio of card width to use for banner (0.0 to 1.0)

        Returns:
            Y position where content should start after the banner
        """
        # Calculate banner width based on ratio
        available_width = self.card_width - (2 * self.margin)
        banner_width = available_width * self.banner_width_ratio
        banner_right_margin = self.margin + (available_width - banner_width)

        # Draw inclined rectangle as polygon with adjustable width
        banner_points = [
            (
                self.margin,
                banner_start_y + self.banner_angle_offset,
            ),  # top-left (lower)
            (
                self.card_width - banner_right_margin,
                banner_start_y,
            ),  # top-right (higher)
            (
                self.card_width - banner_right_margin,
                banner_start_y + self.banner_height,
            ),  # bottom-right
            (
                self.margin,
                banner_start_y + self.banner_height + self.banner_angle_offset,
            ),  # bottom-left (lower)
        ]

        draw.polygon(banner_points, fill=banner_color)
        return banner_start_y + self.banner_height + self.banner_angle_offset + 30

    def add_banner_text(
        self,
        card: Image.Image,
        date: str,
        banner_start_y: int,
        font_type: ImageFont.FreeTypeFont,
    ):
        """
        Add positioned date/time text to the banner based on banner width and position ratio.

        Args:
            card: PIL Image object representing the card
            date: Date string to display on banner
            banner_start_y: Y position where banner starts
        """
        draw = ImageDraw.Draw(card)

        # Calculate banner dimensions
        available_width = self.card_width - (2 * self.margin)
        banner_width = available_width * self.banner_width_ratio
        banner_right_margin = self.margin + (available_width - banner_width)
        banner_left = self.margin
        banner_right = self.card_width - banner_right_margin

        with Pilmoji(card) as pilmoji:
            bbox = draw.textbbox((0, 0), date, font=font_type)
            text_width = bbox[2] - bbox[0]

            # Calculate text position based on banner width and position ratio
            # 0.0 = left aligned within banner, 0.5 = center, 1.0 = right aligned
            banner_text_area = banner_right - banner_left
            available_text_space = banner_text_area - text_width
            text_x = banner_left + (
                available_text_space * self.banner_text_position_ratio
            )

            text_y = (
                banner_start_y
                + (self.banner_height - self.banner_font_size) // 2
                + self.banner_angle_offset // 2
            )

            pilmoji.text(
                (text_x, text_y),
                date,
                font=font_type,
                fill=self.banner_text_color,
            )

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

    def add_event_info(
        self,
        card: Image.Image,
        text: str,
        y_position: int,
        font_type: ImageFont.FreeTypeFont,
        *,
        x_position: int | None = None,
        section_spacing: int | None = None,
        split_text: bool = False,
    ) -> int:
        """Add event type/category with emoji to the card."""
        if split_text:
            return self.split_text(
                card, text, y_position, font_type, x_position=x_position
            )

        x_position = x_position or self.left_margin
        with Pilmoji(card) as pilmoji:
            pilmoji.text(
                (x_position, y_position),
                text,
                font=font_type,
                fill="black",
            )
        return y_position + (section_spacing or self.section_spacing)

    def split_text(
        self,
        card: Image.Image,
        text: str,
        y_position: int,
        font_type: ImageFont.FreeTypeFont,
        *,
        x_position: int | None = None,
        section_spacing: int | None = None,
    ) -> int:
        """Add wrapped event description to the card."""
        draw = ImageDraw.Draw(card)
        max_desc_width = self.card_width - self.left_margin - self.right_margin

        lines = self.wrap_text(text, font_type, max_desc_width, draw)

        x_position = x_position or self.left_margin
        with Pilmoji(card) as pilmoji:
            for i, line in enumerate(lines):
                pilmoji.text(
                    (x_position, y_position + i * self.line_spacing),
                    line,
                    font=font_type,
                    fill="black",
                )

        return (
            y_position
            + len(lines) * self.line_spacing
            + int((section_spacing or self.section_spacing) / 2)
        )

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

    def add_content(
        self, card: Image.Image, event: dict[str, str], content_start_y: int
    ) -> int:
        """Add all event content to the card."""
        y_pos = content_start_y + 20  # Small padding from banner

        y_pos = self.add_event_info(
            card,
            f"🎉 {event['type']}",
            y_pos,
            ImageFont.truetype(self.font_regular, self.type_font_size),
        )
        y_pos = self.add_event_info(
            card,
            event["title"],
            y_pos,
            ImageFont.truetype(self.font_bold, self.title_font_size),
        )
        y_pos = self.add_event_info(
            card,
            event[self._description_key],
            y_pos,
            ImageFont.truetype(self.font_regular, self.desc_font_size),
            split_text=True,
        )
        y_pos = self.add_event_info(
            card,
            event["cost"],
            y_pos,
            ImageFont.truetype(self.font_bold, self.cost_font_size),
            section_spacing=50,
        )
        y_pos = self.add_separator_line(card, y_pos)
        y_pos = self.add_event_info(
            card,
            f"📍 {event['location']}",
            y_pos,
            ImageFont.truetype(self.font_regular, self.location_font_size),
            section_spacing=50,
        )

        return y_pos

    def create_event_card(self, event: dict[str, str], output_path: str):
        """
        Create an event card with standardized design.

        Args:
            event: Dictionary containing event data
            output_path: Path where the generated card image should be saved
        """
        # Create base card
        card = Image.new(
            "RGB", (self.card_width, self.card_height), self.background_color
        )
        draw = ImageDraw.Draw(card)

        # Load and process event image
        banner_start_y = self.load_and_process_image(
            card, event["image"], self.start_card
        )

        # Draw inclined banner
        banner_color = self.get_color(event["date"])
        content_start_y = self.draw_banner(draw, banner_start_y, banner_color)

        # Add banner text
        self.add_banner_text(
            card,
            event["date"],
            banner_start_y,
            ImageFont.truetype(self.font_bold, self.banner_font_size),
        )

        # Add event content
        self.add_content(card, event, content_start_y)

        # Save the card
        card.save(output_path, quality=95)
        print(f"✅ Saved card at {output_path}")
