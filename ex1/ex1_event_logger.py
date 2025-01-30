"""CSC111 EXERCISE 1: Text Adventure Game - Event Logger

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Exercise 1. Please consult
the project handout for instructions and details.

The methods and classes in this file are all REQUIRED. You should complete them exactly
per the provided specification.

Do NOT modify any function/method headers, type contracts, etc. in this class (similar
to CSC110 assignments).

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


@dataclass
class Event:
    """
    A node representing one event in an adventure game.

    Instance Attributes:
    - id_num: Integer id of this event's location
    - description: Long description of this event's location
    - next_command: String command which leads this event to the next event, None if this is the last game event
    - next: Event object representing the next event in the game, or None if this is the last game event
    - prev: Event object representing the previous event in the game, None if this is the first game event
    """

    # NOTES:
    # Complete this class EXACTLY as specified, with ALL of the above attributes.
    # Do NOT add any new attributes, or modify the names or types of the above attributes.
    # If you want to create a special type of Event for your game that requires a different
    # set of attributes, you can do that separately in the project1 folder. This class is part of
    # Exercise 1 and will be auto-graded.
    id_num: int
    description: str
    next_command: Optional[str]
    next: Optional['Event']
    prev: Optional['Event']


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

        if self.is_empty():
            self.first = event
            self.last = event
            event.prev = None
        else:
            self.last.next_command = command
            self.last.next = event
            event.prev = self.last
            self.last = event

    def remove_last_event(self) -> None:
        """Remove the last event from this event list.
        If the list is empty, do nothing."""

        # Hint: The <next_command> and <next> attributes for the new last event should be updated as needed

        if isinstance(self.first) is None:
            return
        elif self.first == self.last:
            self.first = None
            self.last = None
        else:
            self.last = self.last.prev
            self.last.next = None
            self.last.next_command = None

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
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
