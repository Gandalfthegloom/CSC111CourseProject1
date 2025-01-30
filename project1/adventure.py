"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

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
import json
from typing import Optional

from game_entities import Location, Item
from proj1_event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - # TODO add descriptions of public instance attributes as needed

    Representation Invariants:
        - # TODO add any appropriate representation invariants as needed
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int  # Suggested attribute, can be removed
    ongoing: bool  # Suggested attribute, can be removed

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items = self._load_game_data(game_data_file)

        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.current_location_id = initial_location_id  # game begins at this location
        self.ongoing = True  # whether the game is ongoing

    @staticmethod
    def _load_game_data(filename: str) -> tuple[Dict[int, Location], List[str]]:
        """Load locations and items from a JSON file and return structured game data."""
        with open(filename, 'r') as f:
            data = json.load(f)  # Load JSON data

        locations = {}
        for loc_data in data['locations']:
            locations[loc_data['id']] = Location(
                id_num=loc_data['id'],
                name=loc_data['name'],
                brief_description=loc_data['brief_description'],
                long_description=loc_data['long_description'],
                available_commands=loc_data['available_commands'],
                items=loc_data['items']
            )

        return locations, data.get("items", [])  # Ensure items are properly returned


    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """

        # TODO: Complete this method as specified
        if loc_id is None:
            loc_id = self.current_location_id

        return self._locations[loc_id]

    def move(self, direction: str) -> bool:
        """Attempt to move the player in the given direction."""
        current_location = self.get_location()
        if direction in current_location.available_commands:
            new_location_id = current_location.available_commands[direction]
            print(f"Moving from {self.current_location_id} ({current_location.name}) to {new_location_id} ({self.get_location(new_location_id).name})")  # Debugging
            self.current_location_id = new_location_id
            return True
        else:
            print("You can't go that way.")
            return False


if __name__ == "__main__":

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 100)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "score", "undo", "log", "quit"]  # Regular menu options available at each location
    choice = None

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your marks will be based on how well-organized your code is.

        location = game.get_location()

        # TODO: Add new Event to game log to represent current game location
        #  Note that the <choice> variable should be the command which led to this event
        new_event = Event(
            id_num=location.id_num,
            description=location.long_description if not location.visited else location.brief_description,
            next_command=choice,
            next=None,
            prev=None
        )
        game_log.add_event(new_event, choice)
        location.visited = True  # Mark location as visited

        # TODO: Depending on whether or not it's been visited before,
        #  print either full description (first time visit) or brief description (every subsequent visit) of location
        print(location.long_description if not location.visited else location.brief_description)


        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, score, undo, log, quit")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while choice not in location.available_commands and choice not in menu:
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        if choice == "look":
            print(location.long_description)
        elif choice == "inventory":
            inventory_items = [item.name for item in game._items if item.start_position == -1]
            print("Inventory:", ", ".join(inventory_items) if inventory_items else "(empty)")
        elif choice == "score":
            print("Score functionality not yet implemented.")
        elif choice == "undo":
            game_log.remove_last_event()
        elif choice == "log":
            game_log.display_events()
        elif choice == "quit":
            print("Quitting game...")
            game.ongoing = False
            # ENTER YOUR CODE BELOW to handle other menu commands (remember to use helper functions as appropriate)
        else:
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result
            # TODO: Add in code to deal with actions which do not change the location (e.g., taking or using an item)
            if "pick up" in choice:
                item_name = choice.replace("pick up ", "")
                item = next((i for i in game._items if i.name == item_name and i.start_position == game.current_location_id), None)
                if item:
                    item.start_position = -1  # Move item to inventory
                    print(f"You picked up {item.name}!")
                else:
                    print("There's no such item here.")
            elif "use" in choice:
                print("Using items is not implemented yet.")
            else:
                # Handle movement
                game.move(choice)
            # TODO: Add in code to deal with special locations (e.g. puzzles) as needed for your game
