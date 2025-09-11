# Hispanie Event Card Generator

This project generates visually appealing event cards for social media or sharing platforms. The cards include event details such as the title, date, subtitle, description, and location, along with an image.

## Features

- Automatically resizes and centers event images.
- Supports emoji rendering in text fields (e.g., title, description, location).
- Customizable fonts and colors.
- Saves the generated card as a high-quality image.

## Requirements

- Python 3.12+
- Required Python libraries:
  - `Pillow`
  - `requests`
  - `pilmoji`

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hispanie_event_card
   ```

## Setting Up a Virtual Environment

It is recommended to use a virtual environment to manage dependencies and isolate the project environment.

1. Ensure you have Python 3.12 or higher installed. Check your Python version:

   ```bash
   python3 --version
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Now your virtual environment is ready, and you can run the script as described in the [Usage](#usage) section.

## Usage

1. Prepare your event details in a dictionary format. Example:
   ```python
   event = {
       "image": "https://example.com/event_image.jpg",
       "title": "SALSA SUR LES QUAIS",
       "date": "MERCREDI - 20H À 23H",
       "subtitle": "Soirée Latine 💃",
       "description": "Salsa sur les Quais s’installe le temps d’une soirée sous les Nefs. Un lieu unique, atypique voire magiiiiiiiiiiique ✨✨✨",
       "location": "📍 Machines de l'île de Nantes",
   }
   ```
2. Run the script to generate the event card:
   ```bash
   python event_card_generator.py
   ```
3. The generated card will be saved in the `images` folder as `output_event_card.jpg`.

## Customization

- **Fonts**: Update the `FONT_BOLD` and `FONT_REGULAR` variables in `event_card_generator.py` to use your preferred font files.
- **Card Dimensions**: Modify `CARD_WIDTH` and `CARD_HEIGHT` to adjust the size of the card.
- **Colors**: Change the `banner_color` logic to customize the banner colors.

## Example Output

The generated card will look like this:
![Example Event Card](images/output_event_card.jpg)

## License

This project is licensed under the MIT License.
