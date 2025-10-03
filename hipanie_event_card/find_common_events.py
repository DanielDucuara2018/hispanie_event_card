import json
import logging
from pathlib import Path
from typing import Any

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


class EventMerger:
    """Class to handle event merging operations."""

    def __init__(self):
        self.common_events = []
        self.common_links = set()

    def load_json_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Load JSON file and return the data."""
        try:
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []

    def create_link_map(
        self, events: list[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        """Create a mapping of links to events."""
        return {
            link: event
            for event in events
            if (link := event.get("link", "").strip()) and link != "not found"
        }

    def merge_single_event(
        self, non_detailed_event: dict[str, Any], detailed_event: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge two events, overwriting specific fields from source to base."""
        merged_event = non_detailed_event.copy()

        fields_to_overwrite = [
            "title",
            "location",
            "description_short",
            "description_long",
            "cost",
            "type",
        ]

        for field in fields_to_overwrite:
            source_value = detailed_event.get(field, "").strip()
            if source_value and source_value != "not found":
                merged_event[field] = source_value

        return merged_event

    def find_common_links(
        self,
        non_detailed_link_map: dict[str, dict[str, Any]],
        detailed_link_map: dict[str, dict[str, Any]],
    ) -> set[str]:
        """Find common links between two link maps."""
        common_links = set(non_detailed_link_map) & set(detailed_link_map)
        logger.info(f"Found {len(common_links)} common events")
        return common_links

    def merge_common_events(
        self,
        non_detailed_link_map: dict[str, dict[str, Any]],
        detailed_link_map: dict[str, dict[str, Any]],
        common_links: set[str],
    ) -> list[dict[str, Any]]:
        """Merge all common events and return the list."""
        common_events = []

        for link in common_links:
            non_detailed_event = non_detailed_link_map[link]
            detailed_event = detailed_link_map[link]

            merged_event = self.merge_single_event(non_detailed_event, detailed_event)
            common_events.append(merged_event)

            logger.info(
                f"Merged event: {merged_event.get('title', 'No title')[:50]}..."
            )

        return common_events

    def filter_non_common_events(
        self, events_non_detailed: list[dict[str, Any]], common_links: set[str]
    ) -> list[dict[str, Any]]:
        """Filter out common events from the original events list."""
        non_common_events = [
            event
            for event in events_non_detailed
            if event.get("link", "").strip() not in common_links
        ]

        logger.info(
            f"Found {len(non_common_events)} non-common events to keep in events_non_detailed.json"
        )
        return non_common_events

    def sort_events_by_date(self, events: list) -> list:
        """Sort events by start date if available."""
        try:
            return sorted(events, key=lambda x: x.get("start_dt", ""))
        except Exception:
            return events

    def save_events_to_file(
        self, events: list, file_path: Path, description: str
    ) -> None:
        """Save events list to JSON file."""
        try:
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(events, f, ensure_ascii=False, indent=4)
            logger.info(
                f"✅ Successfully {description} {file_path} with {len(events)} events"
            )
        except Exception as e:
            logger.error(f"❌ Error saving to {file_path}: {e}")

    def load_and_validate_files(
        self, events_non_detailed_file: Path, events_detailed_file: Path
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Load both JSON files and return their contents."""
        logger.info("Loading JSON files...")

        events_non_detailed = self.load_json_file(events_non_detailed_file)
        events_detailed = self.load_json_file(events_detailed_file)

        logger.info(
            f"Loaded {len(events_non_detailed)} events from events_non_detailed.json"
        )
        logger.info(f"Loaded {len(events_detailed)} events from events_detailed.json")

        return events_non_detailed, events_detailed

    def create_link_maps(
        self,
        events_non_detailed: list[dict[str, Any]],
        events_detailed: list[dict[str, Any]],
    ) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        """Create link maps for both event lists."""
        non_detailed_link_map = self.create_link_map(events_non_detailed)
        detailed_link_map = self.create_link_map(events_detailed)

        logger.info(
            f"Found {len(non_detailed_link_map)} events with valid links in events_non_detailed.json"
        )
        logger.info(
            f"Found {len(detailed_link_map)} events with valid links in events_detailed.json"
        )

        return non_detailed_link_map, detailed_link_map

    def process_and_save_events(
        self,
        common_events: list[dict[str, Any]],
        non_common_events: list[dict[str, Any]],
        output_file: Path,
        events_non_detailed_file: Path,
    ) -> None:
        """Sort and save both common and non-common events."""
        # Sort events by date
        common_events = self.sort_events_by_date(common_events)
        non_common_events = self.sort_events_by_date(non_common_events)

        # Save files
        self.save_events_to_file(common_events, output_file, "created")
        self.save_events_to_file(non_common_events, events_non_detailed_file, "updated")

    def find_and_merge_common_events(
        self,
        events_non_detailed_file: Path,
        events_detailed_file: Path,
        output_file: Path,
    ) -> None:
        """Find common events between two JSON files and create merged events.json file."""
        # Load and validate files
        events_non_detailed, events_detailed = self.load_and_validate_files(
            events_non_detailed_file, events_detailed_file
        )

        # Create link maps
        non_detailed_link_map, detailed_link_map = self.create_link_maps(
            events_non_detailed, events_detailed
        )

        # Find common links
        common_links = self.find_common_links(non_detailed_link_map, detailed_link_map)

        # Merge common events
        common_events = self.merge_common_events(
            non_detailed_link_map, detailed_link_map, common_links
        )

        # Filter non-common events
        non_common_events = self.filter_non_common_events(
            events_non_detailed, common_links
        )

        # Process and save results
        self.process_and_save_events(
            common_events, non_common_events, output_file, events_non_detailed_file
        )


def validate_input_files(
    events_non_detailed_file: Path, events_detailed_file: Path
) -> bool:
    """Validate that input files exist."""
    if not events_non_detailed_file.exists():
        logger.error(f"❌ File not found: {events_non_detailed_file}")
        return False

    if not events_detailed_file.exists():
        logger.error(f"❌ File not found: {events_detailed_file}")
        return False

    return True


def print_summary(
    events_non_detailed_file: Path, events_detailed_file: Path, output_file: Path
) -> None:
    """Print process summary."""
    logger.info("\n📊 Summary:")
    logger.info(
        f"Base file: {events_non_detailed_file} (updated to contain only non-common events)"
    )
    logger.info(f"Source file: {events_detailed_file}")
    logger.info(f"Output file: {output_file} (contains merged common events)")
    logger.info(
        "\nFields overwritten from source: title, location, description_short, description_long, cost, type"
    )


def main():
    """Main function to run the event merging process."""
    # Define file paths
    base_dir = Path(__file__).parent
    input_folder = base_dir.joinpath("input")

    events_non_detailed_file = input_folder.joinpath("events_paris.json")
    events_detailed_file = input_folder.joinpath("events_paris_detailed.json")
    output_file = input_folder.joinpath("events.json")

    # Validate input files
    if not validate_input_files(events_non_detailed_file, events_detailed_file):
        return

    # Process the files
    merger = EventMerger()
    merger.find_and_merge_common_events(
        events_non_detailed_file, events_detailed_file, output_file
    )

    # Print summary
    print_summary(events_non_detailed_file, events_detailed_file, output_file)


if __name__ == "__main__":
    main()
