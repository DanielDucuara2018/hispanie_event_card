import json
import logging
from pathlib import Path
from typing import Any

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def load_json_file(file_path: Path) -> list[dict[str, Any]]:
    """
    Load JSON file and return the data.

    Args:
        file_path: Path to the JSON file

    Returns:
        list of event dictionaries
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return []


def create_link_map(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Create a mapping of links to events.

    Args:
        events: list of event dictionaries

    Returns:
        dictionary mapping links to events
    """
    link_map = {}
    for event in events:
        link = event.get("link", "").strip()
        if link and link != "not found":
            link_map[link] = event
    return link_map


def merge_events(
    base_event: dict[str, Any], source_event: dict[str, Any]
) -> dict[str, Any]:
    """
    Merge two events, overwriting specific fields from source to base.

    Args:
        base_event: Base event from events_paris.json
        source_event: Source event from events_paris_20250915_20250921.json

    Returns:
        Merged event dictionary
    """
    # Start with base event
    merged_event = base_event.copy()

    # Fields to overwrite from source event
    fields_to_overwrite = [
        "title",
        "location",
        "description_short",
        "description_long",
        "cost",
        "type",
    ]

    for field in fields_to_overwrite:
        source_value = source_event.get(field, "").strip()
        if source_value and source_value != "not found":
            merged_event[field] = source_value

    return merged_event


def find_and_merge_common_events(
    events_paris_file: Path, events_detailed_file: Path, output_file: Path
) -> None:
    """
    Find common events between two JSON files and create merged events.json file.
    Also update events_paris.json to remove common events.

    Args:
        events_paris_file: Path to events_paris.json
        events_detailed_file: Path to events_paris_20250915_20250921.json
        output_file: Path to output events.json file
    """
    logger.info("Loading JSON files...")

    # Load both JSON files
    events_paris = load_json_file(events_paris_file)
    events_detailed = load_json_file(events_detailed_file)

    logger.info(f"Loaded {len(events_paris)} events from events_paris.json")
    logger.info(
        f"Loaded {len(events_detailed)} events from events_paris_20250915_20250921.json"
    )

    # Create link maps
    paris_link_map = create_link_map(events_paris)
    detailed_link_map = create_link_map(events_detailed)

    logger.info(
        f"Found {len(paris_link_map)} events with valid links in events_paris.json"
    )
    logger.info(
        f"Found {len(detailed_link_map)} events with valid links in events_paris_20250915_20250921.json"
    )

    # Find common events based on links
    common_events = []
    common_links = set(paris_link_map) & set(detailed_link_map)

    logger.info(f"Found {len(common_links)} common events")

    for link in common_links:
        base_event = paris_link_map[link]
        source_event = detailed_link_map[link]

        # Merge events
        merged_event = merge_events(base_event, source_event)
        common_events.append(merged_event)

        logger.info(f"Merged event: {merged_event.get('title', 'No title')[:50]}...")

    # Create list of non-common events from events_paris.json
    non_common_events = []
    for event in events_paris:
        event_link = event.get("link", "").strip()
        if event_link not in common_links:
            non_common_events.append(event)

    logger.info(
        f"Found {len(non_common_events)} non-common events to keep in events_paris.json"
    )

    # Sort events by date if available
    try:
        common_events.sort(key=lambda x: x.get("start_dt", ""))
        non_common_events.sort(key=lambda x: x.get("start_dt", ""))
    except Exception:
        pass

    # Save merged common events to output file
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(common_events, f, ensure_ascii=False, indent=4)
        logger.info(
            f"✅ Successfully created {output_file} with {len(common_events)} common events"
        )
    except Exception as e:
        logger.error(f"❌ Error saving to {output_file}: {e}")

    # Update events_paris.json with only non-common events
    try:
        with events_paris_file.open("w", encoding="utf-8") as f:
            json.dump(non_common_events, f, ensure_ascii=False, indent=4)
        logger.info(
            f"✅ Updated {events_paris_file} with {len(non_common_events)} non-common events"
        )
    except Exception as e:
        logger.error(f"❌ Error updating {events_paris_file}: {e}")


def main():
    """Main function to run the event merging process."""

    # Define file paths
    base_dir = Path(__file__).parent
    input_folder = base_dir.joinpath("input")

    events_paris_file = input_folder.joinpath("events_paris.json")
    events_detailed_file = input_folder.joinpath("events_paris_20250915_20250921.json")
    output_file = input_folder.joinpath("events.json")

    # Check if input files exist
    if not events_paris_file.exists():
        logger.error(f"❌ File not found: {events_paris_file}")
        return

    if not events_detailed_file.exists():
        logger.error(f"❌ File not found: {events_detailed_file}")
        return

    # Process the files
    find_and_merge_common_events(events_paris_file, events_detailed_file, output_file)

    logger.info("\n📊 Summary:")
    logger.info(
        f"Base file: {events_paris_file} (updated to contain only non-common events)"
    )
    logger.info(f"Source file: {events_detailed_file}")
    logger.info(f"Output file: {output_file} (contains merged common events)")
    logger.info(
        "\nFields overwritten from source: title, location, description_short, description_long, cost, type"
    )


if __name__ == "__main__":
    main()
