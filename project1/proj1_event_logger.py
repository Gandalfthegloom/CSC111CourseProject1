"""CSC111 Project 1: Text Adventure Game - Event Logger

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

You can copy/paste your code from the ex1_simulation file into this one, and modify it as needed
to work with your game.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# TODO: Copy/paste your ex1_event_logger code below, and modify it if needed to fit your game


@dataclass
class Event:
    """
    A node representing one event in an adventure game.
    """
    id_num: int
    description: str
    next_command: Optional[str]
    next: Optional['Event']
    prev: Optional['Event']
    item_affected: Optional[str] = None  # Track the item affected (if any)
    item_prev_location: Optional[int] = None  # Store where the item was before the action
    score_change: int = 0


class EventList:
    """
    A linked list of game events.

    # TODO add descriptions of instance attributes here
    Instance Attributes:
        - first: points towards (or contains) the first event in the list.
        - last: points towards (or contains) the last event in the list.

    # TODO add any appropriate representation invariants, if needed
    Representation Invariants:
        - (self.first is None and self.last is None) or (self.first is not None and self.last is not None)
    """
    first: Optional[Event]
    last: Optional[Event]

    def __init__(self) -> None:
        """Initialize a new empty event list."""

        self.first = None
        self.last = None

    def display_events(self) -> None:
        """Display all events in chronological order."""
        curr = self.first
        while curr:
            print(f"Location: {curr.id_num}, Command: {curr.next_command}")
            curr = curr.next

    #  That is, the function headers (parameters, return type, etc.) must NOT be changed.
    def is_empty(self) -> bool:
        """Return whether this event list is empty."""

        return self.first is None

    def add_event(self, event: Event, command: Optional[str] = None) -> None:
        """Add the given new event to the end of this event list.
        The given command is the command which was used to reach this new event, or None if this is the first
        event in the game.
        """
        # Hint: You should update the previous node's <next_command> as needed

        event.next_command = command

        if self.is_empty():
            self.first = event
            self.last = event
            event.prev = None
        else:
            event.prev = self.last
            self.last.next = event
            self.last = event

    def remove_last_event(self, score_ref: dict) -> Optional[Event]:
        """Remove the last event from this event list, reverting any item changes if necessary."""
        if self.is_empty():
            return None

        removed_event = self.last

        if self.first == self.last:  # If there's only one event
            self.first = None
            self.last = None
        else:
            self.last = self.last.prev
            self.last.next = None
            self.last.next_command = None

        if removed_event.score_change:
            score_ref['score'] -= removed_event.score_change  # Mutation hell yeah
            print(f"Score reverted by {removed_event.score_change}. New score: {score_ref['score']}")

        return removed_event

    def get_id_log(self) -> list[int]:
        """Return a list of all location IDs visited for each event in this list, in sequence."""

        event = self.first
        id_list = []
        while event is not None:
            id_list.append(event.id_num)
            event = event.next
        return id_list

    # Note: You may add other methods to this class as needed but DO NOT CHANGE THE SPECIFICATION OF ANY OF THE ABOVE


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
