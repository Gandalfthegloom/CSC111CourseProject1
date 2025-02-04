"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate an entire
playthrough of the game. Please consult the project handout for instructions and details.

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
from proj1_event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location, Puzzle


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
            next_command='start',  # Change from None to 'start'
            next=None,
            prev=None,
            state_snapshot={}
        ), command=None)

        self.generate_events(commands)

    def generate_events(self, commands: list[str]) -> None:
        """Generate all events based on the given list of commands."""
        for command in commands:
            if not self.process_command(command):
                print(f"Invalid command: {command}")

    def process_command(self, command: str) -> bool:
        """Process a single command and generate the corresponding event."""
        current_location = self._game.get_location()

        if isinstance(current_location, Puzzle):
            # TODO
        if command in current_location.available_commands:
            self._game.move(command)
        elif command.startswith("pick up ") or command.startswith("use ") or command.startswith("drop "):
            self._game.process_game_command(command, self._game, self._events)
        elif command in ["look", "inventory", "score", "undo", "log", "quit", "time", "objective", "toggledebug"]:
            self._game.process_menu_command(command, self._game, self._events)
        else:
            return False

        self._game.handle_location_visit(self._events)

        new_location = self._game.get_location()
        new_event = Event(
            id_num=new_location.id_num,
            description=new_location.get_description(),
            next_command=command,
            next=None,
            prev=None,
            state_snapshot={}
        )
        self._events.add_event(new_event, command)
        return True

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
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })

    # TODO: Modify the code below to provide a walkthrough of commands needed to win and lose the game
    win_walkthrough = [
        "turn off alarm", "wake up", "check alarm label", "next", "read note",
        "flip out", "calm down", "walk out", "wear pants",
        "prepare to go out", "pick up wallet", "pick up bag",
        "go west", "go north", "go north",
        "go east", "order coffee", "grab napkin", "flip napkin", "prepare to go out",
        "go west", "go east", "go west", "go south", "go south", "go south",
        "go west", "next", "go upstairs", "go left", "go right", "ok",
        "use wallet", "turn back", "go east", "go forward", "use mysterious key", "password",
        "sdvvzrug", "leave", "go back", "go downstairs",
        "go north", "use mysterious-er key", "investigate", "enter password", "73691",
        "next", "use bag", "next", "go out", "go upstairs", "go left", "go right",
        "look", "pick up laptop charger", "go east", "go back", "go downstairs",
        "go out", "go north", "go north", "go north", "go north",
        "go west", "look around", "look", "pick up library pamphlet", "use library pamphlet",
        "next", "look around", "go upstairs", "go upstairs", "look",
        "pick up blue pamphlet first page", "examine blue pamphlet first page",
        "go downstairs", "go downstairs", "go east", "go upstairs", "look",
        "pick up blue pamphlet second page", "use blue pamphlet second page", "inquire",
        "return to the realm of the living", "go up to stack", "13", "mathematics",
        "computer science", "python", "exit",
        "go east", "go east", "go east", "go east", "go east", "go east", "exit",
        "go south", "help", "weed killer", "trowel", "continue",
        "continue walking", "go south", "go west", "continue walking", "go south",
        "go south", "continue", "look", "pick up comically long stick",
        "use comically long stick", "continue", "go north", "go east", "look",
        "use dog whistle", "continue walking", "go north", "go north", "go west",
        "go south", "look", "use dog whistle", "use winnie the poodle",
        "continue walking", "continue", "look", "use shoddy shovel", "celebrate",
        "submit", "grab object", "pass the torch"]

    expected_log = [
        10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009,
        100, 100, 100,
        303, 302, 301,
        1100, 110002, 110003, 110004, 1100,
        301, 1100, 301, 302, 303, 304,
        1600, 1600, 1601, 1604, 1608, 1608,
        160003, 1608, 1604, 1607, 160004, 160005, 1604, 1601, 1600,
        1602, 160006, 160007, 160017, 160018,
        1602, 160019, 1602, 1600, 1601, 1604, 1608, 1608, 1608, 1604, 1601, 1600,
        304, 303, 302, 301, 500,
        200, 200, 200, 200,
        20002, 20003,
        201, 202, 203, 203, 203, 202, 201, 200,
        210, 210, 210,
        21001, 21001,
        200, 205, 206, 207, 208, 20004, 200,
        500, 401, 402, 403, 800, 1001, 1001,
        1002, 100006, 100007, 100010, 100011,
        1002, 1003,
        902, 902, 903, 700, 700, 700, 700, 100013, 700,
        903, 1004, 1004, 100003, 1004, 1003, 1002,
        901, 902, 902, 902, 100004, 902, 1001, 1001, 100015, 1001, 10011, 10012, 99999]
    # Uncomment the line below to test your walkthrough
    assert expected_log == AdventureGameSimulation('game_data.json', 1, win_walkthrough)

    # Create a list of all the commands needed to walk through your game to reach a 'game over' state
    lose_demo = []
    expected_log = []  # Update this log list to include the IDs of all locations that would be visited
    # Uncomment the line below to test your demo
    # assert expected_log == AdventureGameSimulation('game_data.json', 1, lose_demo)

    # TODO: Add code below to provide walkthroughs that show off certain features of the game
    # TODO: Create a list of commands involving visiting locations, picking up items, and then
    #   checking the inventory, your list must include the "inventory" command at least once
    # inventory_demo = [..., "inventory", ...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # scores_demo = [..., "score", ...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # Add more enhancement_demos if you have more enhancements
    # enhancement1_demo = [...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # Note: You can add more code below for your own testing purposes
