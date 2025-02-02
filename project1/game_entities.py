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

@dataclass
class Location:
    """A location in our text adventure game world."""

    id_num: int
    name: str
    brief_description: str
    long_description: str
    available_commands: Dict[str, int]  # Dictionary mapping directions to location IDs
    items: List[str]  # List of item names present in this location
    extra_description: Optional[str] = None  # New field for additional details
    visited: bool = False  # Tracks if player has been here before
    looked: bool = False # Tracks if player has looked here before
    first_time_event_id: Optional[int] = None
    is_locked: bool = False# Check whether room is locked
    unlock_condition: Optional[str] = None # If locked, unlock requirement.

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
    """An item in our text adventure game world.

    Instance Attributes:
        - # TODO Describe each instance attribute here

    Representation Invariants:
        - # TODO Describe any necessary representation invariants
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
    current_position: Optional[int] = None  # Inventory tracking
    use_location: Optional[int] = None  # Location ID where this item can be used
    triggers_event_id: Optional[int] = None  # ID of the StoryEvent triggered when used

# New StoryEvent class inheriting from Event
from proj1_event_logger import Event


@dataclass
class StoryEvent(Location):
    """A story event that functions like a location, allowing for narrative-driven choices."""

    story_text: Optional[Union[str, List[str]]] = None  # Allow story_text to be a list or a string
    choices: Optional[List[str]] = None  # List of available choices
    new_objective: Optional[str] = None # For objective command

    def get_description(self) -> str:
        """Display the story text instead of regular location descriptions."""
        if isinstance(self.story_text, list):
            return "\n".join(self.story_text)  # Join list elements into a multi-line string
        return self.story_text if self.story_text else super().get_description()

# Example Puzzle Functions
def caesar_cipher_puzzle() -> bool:
    """Simulates solving a Caesar cipher puzzle."""
    user_input = input("Enter the 5-letter code to unlock the safe: ").strip().upper()
    return user_input == "JULIUS"

def mirror_riddle_puzzle() -> bool:
    """Simulates solving the mirror reflection riddle."""
    user_input = input("What do you do after reading the reversed note? ").strip().lower()
    return user_input == "check bag"

def shadow_projection_puzzle() -> bool:
    """Simulates solving the projection shadow puzzle."""
    user_input = input("What location do the unshadowed letters spell out? ").strip().lower()
    return user_input == "bathroom"


if __name__ == "__main__":
    pass
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })
