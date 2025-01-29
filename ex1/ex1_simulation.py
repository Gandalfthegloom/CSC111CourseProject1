"""CSC111 Exercise 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Exercise 1 that allows a user to simulate the
playthrough of the game. Please consult the project handout for instructions and details.

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
from proj1_event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location

class AdventureGameSimulation:
    """A simulation of an adventure game playthrough."""
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """Initialize a new game simulation with a list of commands."""
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)
        initial_location = self._game.get_location()
        
        # Add first event
        self._events.add_event(Event(
            id_num=initial_location.id_num,
            description=initial_location.long_description,
            next_command=None,
            next=None,
            prev=None
        ), command=None)
        
        self.generate_events(commands, initial_location)

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """Generate all events based on the given list of commands."""
        for command in commands:
            if command in current_location.available_commands:
                next_loc_id = current_location.available_commands[command]
                next_loc = self._game.get_location(next_loc_id)
                new_event = Event(
                    id_num=next_loc.id_num,
                    description=next_loc.long_description,
                    next_command=command,
                    next=None,
                    prev=None
                )  
                self._events.add_event(new_event, command)
                current_location = next_loc
            else:
                print(f"Invalid command: {command}")

    def get_id_log(self) -> list[int]:
        """Return a list of all visited location IDs."""
        return self._events.get_id_log()

    def run(self) -> None:
        """Run the game simulation and print location descriptions."""
        current_event = self._events.first
        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You chose:", current_event.next_command)
            current_event = current_event.next



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
