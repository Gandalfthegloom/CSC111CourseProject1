"""CSC111 Project 1: Text Adventure Game - Game Entities

Instructions (READ THIS FIRST!)
===============================

This Python module contains the entity classes for Project 1, to be imported and used by
 the `adventure` module.
 Please consult the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
import textwrap

import os
import sys
import subprocess  # For inquire


@dataclass
class Location:
    """
    A location in our text adventure game world.

    Instance Attributes:
        - id_num:
            A unique integer identifier for this location.
        - name:
            The name of the location.
        - brief_description:
            A short description used after the location has been visited.
        - long_description:
            A detailed description shown the first time the location is visited.
        - available_commands:
            A dictionary mapping available command strings (e.g., directions)
            to the corresponding location IDs.
        - items:
            A list of item names present in this location.
        - extra_description:
            Optional extra details about the location.
        - visited:
            Whether the player has visited this location before.
        - looked:
            Whether the player has examined this location (looked around).
        - first_time_event_id:
            Optional event ID that should trigger on the first visit.
        - is_locked:
            Indicates whether the location is locked.
        - unlock_condition:
            An optional condition (as a string expression) that must be met
            to unlock the location.

    Representation Invariants:
        - id_num is an integer and unique among locations.
        - available_commands maps strings to integer location IDs.
        - visited and looked are booleans.
        - If is_locked is True, then unlock_condition should be a non-empty string
          (unless it is intentionally left as None to indicate no unlock condition).
    """

    id_num: int
    name: str
    brief_description: str
    long_description: str
    available_commands: Dict[str, int]  # Dictionary mapping directions to location IDs
    items: List[str]  # List of item names present in this location
    extra_description: Optional[str] = None  # New field for additional details
    visited: bool = False  # Tracks if player has been here before
    looked: bool = False  # Tracks if player has looked here before
    first_time_event_id: Optional[int] = None
    is_locked: bool = False  # Check whether room is locked
    unlock_condition: Optional[str] = None  # If locked, unlock requirement.

    def get_description(self) -> str:
        """Return the appropriate description based on whether this location has been visited."""
        description = self.long_description if not self.visited else self.brief_description
        return textwrap.fill(description, width=160)

    def look_around(self) -> str:
        """Return additional details if available, otherwise return a generic response."""
        extra = self.extra_description if self.extra_description else "You find nothing of note."
        return textwrap.fill(extra, width=160)


@dataclass
class Item:
    """An item in our text adventure game world :D.
    Instance Attributes:
        name:
            The name of the item.
        start_position:
            The location ID where the item initially appears.
        target_position:
            The location ID where the item is meant to be used or delivered.
        target_points:
            The points awarded to the player when the item is used correctly.
        description:
            A textual description of the item.
        current_position:
            The current location of the item, or -1 if the item is in the player's inventory.
        use_location:
            The location ID where this item can be used.
        triggers_event_id:
            The ID of the StoryEvent that is triggered when the item is used.

    Representation Invariants:
        - start_position and target_position are integers.
        - target_points is an integer and is non-negative.
        - current_position is either -1 (indicating inventory) or a valid location ID.
    """

    # NOTES:
    # This is just a suggested starter class for Item.
    # You may change these parameters and the data available for each Item object as you see fit.
    # (The current parameters correspond to the example in the handout).
    #
    # The only thing you must NOT change is the name of this class: Item.
    # All item objects in your game MUST be represented as an instance of this class.

    name: str
    start_position: int
    target_position: int
    target_points: int
    description: Optional[str] = None
    current_position: Optional[int] = None  # Inventory tracking
    use_location: Optional[int] = None  # Location ID where this item can be used
    triggers_event_id: Optional[int] = None  # ID of the StoryEvent triggered when used


@dataclass
class Puzzle(Location):
    """
    A puzzle location where the player must enter a password to proceed.
    Inherits from Location, so all location attributes apply.

    Instance Attributes (in addition to Location attributes):
        - puzzle_text:
            The text(s) describing the puzzle to be solved.
        - choices:
            Optional list of choices available for the puzzle.
        - answers:
            A list of valid answers (e.g., passwords) that solve the puzzle.

    Representation Invariants:
        - puzzle_text is either a string or a list of strings.
        - If answers is provided, it is a non-empty list of strings
    """
    puzzle_text: Optional[Union[str, List[str]]] = None
    choices: Optional[List[str]] = None
    answers: Optional[List[str]] = None

    def get_description(self) -> str:
        """Return the puzzle text as the description."""
        return "\n".join(self.puzzle_text)


@dataclass
class StoryEvent(Location):
    """
    A story event that functions like a location, allowing for narrative-driven choices.
    Inherits from Location, so all location attributes apply.
    Designed to only be accessed once per playtrough.

    Instance Attributes:
        - story_text:
            The narrative associated with the event. Can be either a string or a list of strings.
        - choices:
            A list of available choices for the event.
        - new_objective:
            A new objective that replaces the current one when this event is triggered.
        - trigger_condition:
            A string expression representing the condition under which the event should be triggered.
            This is evaluated based on the player's inventory.

    Representation Invariants:
        - If story_text is a list, it should contain at least one string.
        - trigger_condition, if provided, should be a valid Python expression that can be evaluated
          in a context where 'inventory' is defined.
          """

    story_text: Optional[Union[str, List[str]]] = None  # Allow story_text to be a list or a string
    choices: Optional[List[str]] = None  # List of available choices
    new_objective: Optional[str] = None  # For objective command
    trigger_condition: Optional[str] = None

    def get_description(self) -> str:
        """Display the story text instead of regular location descriptions."""
        if isinstance(self.story_text, list):
            return "\n".join(self.story_text)  # Join list elements into a multi-line string
        return self.story_text if self.story_text else super().get_description()


def inquire() -> None:
    """
    Opens an outline pdf file for the Library of Congress Index.
    All hail Stack Overflow!
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, "loc_outline.pdf")

    if sys.platform.startswith('win'):
        # On Windows, use os.startfile to open the file with its associated application
        os.startfile(pdf_path)
    elif sys.platform.startswith('darwin'):
        # On macOS, use the 'open' command via subprocess
        subprocess.run(["open", pdf_path], check=True)
    else:
        # On Linux or Unix-like systems, use 'xdg-open'
        subprocess.run(["xdg-open", pdf_path], check=True)


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
