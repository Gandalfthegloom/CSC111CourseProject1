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
from typing import Dict, List, Optional

from scripts.regsetup import description

from game_entities import Location, Item, StoryEvent, Puzzle
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

    debug_mode = False  # Class-level attribute to toggle debug mode
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
        self._locations, self._items, self._stories, self._puzzle = self._load_game_data(game_data_file)

        # Initialize to 3:00 PM (15*60 minutes)
        self.current_time = 15 * 60

        # Initialize score to 0
        self.score = 0

        # Set player objective
        self.current_objective = "Find your missing project items before 4 PM."

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
                brief_description=loc_data.get('brief_description', ""),
                long_description=loc_data.get('brief_description', ""),
                available_commands=loc_data['available_commands'],
                items=loc_data['items'],
                extra_description=loc_data.get('extra_description', None),
                first_time_event_id=loc_data.get('first_time_event_id', None),
                is_locked=loc_data.get('is_locked', False),
                unlock_condition=loc_data.get('unlock_condition', None)
            )

        items = [Item(
            name=item_data["name"],
            start_position=item_data["start_position"],
            target_position=item_data.get("target_position", -1),  # Default target location
            description=item_data.get("description", ""),
            target_points=item_data.get("target_points", 0),  # Default points
            current_position=item_data.get("current_position", item_data["start_position"]),
            use_location=item_data.get("use_location", None),
            triggers_event_id=item_data.get("triggers_event_id", None)
        ) for item_data in data.get("items", [])]

        # Load story events
        stories = {
            story_data['id']: StoryEvent(
                id_num=story_data['id'],
                name=story_data['name'],
                brief_description=story_data.get('brief_description', ''),
                long_description=story_data.get('long_description', ''),
                available_commands=story_data['available_commands'],
                items=story_data.get('items', []),
                story_text=story_data.get('story_text', ""),
                choices=story_data.get('choices', []),
                new_objective=story_data.get('new_objective', None)
            ) for story_data in data.get('story_events', [])
        }

        # Load puzzles
        puzzles = {
            puzzle_data['id']: Puzzle(
                id_num=puzzle_data['id'],
                name=puzzle_data['name'],
                brief_description='',
                long_description='',
                available_commands=puzzle_data['available_commands'],
                items=puzzle_data.get('items', []),
                puzzle_text=puzzle_data['puzzle_text'],
                answers=puzzle_data.get('answers', []),
            ) for puzzle_data in data.get('puzzle', [])
        }


        return locations, items, stories, puzzles

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """

        if loc_id is None:
            loc_id = self.current_location_id

        if loc_id in self._stories:
            return self._stories[loc_id]
        elif loc_id in self._locations:
            return self._locations[loc_id]
        elif loc_id in self._puzzle:
            return self._puzzle[loc_id]
        else:
            raise KeyError(f"Location ID {loc_id} not found in locations or story events.")

    def move(self, direction: str) -> bool:
        current_location = self.get_location()

        if direction not in current_location.available_commands:
            print("You can't go that way.")
            return False

        new_location_id = current_location.available_commands[direction]
        new_location = self.get_location(new_location_id)

        # Check if the new location is locked
        if new_location.is_locked:
            if self._evaluate_unlock_condition(new_location.unlock_condition):
                new_location.is_locked = False
                print(f"You've unlocked {new_location.name}!")
            else:
                print(
                    f"{new_location.name} is locked. {'You need to fulfill the unlock condition.'}")

        # Handle Puzzle-specific movement (e.g., password)
        if isinstance(current_location, Puzzle) and direction != "password":
            if isinstance(current_location, Puzzle) and direction != "password":
                new_location_id = current_location.available_commands[direction]
                self.current_location_id = new_location_id
                print(f"You move to {self.get_location().name}.")
                return True
            elif isinstance(current_location, Puzzle):
                # Prevent automatic puzzle solving during movement
                print("This location requires a password to proceed. Use the 'password' command to attempt it.")
                return False
            else:
                new_location_id = current_location.available_commands[direction]
                self.current_location_id = new_location_id
                print(f"You move to {self.get_location().name}.")
                return True

        # Proceed with moving to the new location
        self.current_location_id = new_location_id
        print(f"You move to {new_location.name}.")

        # Update game time for regular locations
        if not isinstance(new_location, StoryEvent):
            self.current_time += 2

        # Check for game over due to time
        if self.current_time >= 16 * 60:
            print("\nYou've run out of time! It's now past 4:00 PM. Game Over.")
            self.ongoing = False

        return True


    def _evaluate_unlock_condition(self, condition: Optional[str]) -> bool:
        """Evaluate if the unlock condition is met."""
        if not condition:
            return False

        inventory = [item.name.lower() for item in self._items if item.current_position == -1]
        try:
            # Use eval carefully to avoid security risks
            return eval(condition, {}, {"inventory": inventory})
        except Exception as e:
            print(f"Error evaluating unlock condition: {e}")
            return False

    def _handle_movement(self, choice: str, game: AdventureGame) -> None:
        """Handle movement between locations."""
        if choice in game.get_location().available_commands:
            game.move(choice)
        else:
            print("Invalid movement command.")

    def _handle_location_visit(self) -> None:
        """Handle visiting a location or triggering a story event."""
        location = self.get_location()

        # If it's a StoryEvent, display story content
        if isinstance(location, StoryEvent):
            print(location.get_description())
            # Give items from the story event
            for item_name in location.items:
                item = next((i for i in self._items if i.name == item_name), None)
                if item:
                    item.current_position = -1  # Add to inventory
                    print(f"You received {item.name}!")
            if isinstance(location.new_objective, str):
                self.current_objective = location.new_objective
            if location.name == "Game Over":
                self.ongoing = False
                print("Game Over. Better luck next time!")
                exit()
            return

        # Handle first-time story event trigger for regular locations
        if not location.visited:
            self.score += 5
            if location.first_time_event_id:
                self.current_location_id = location.first_time_event_id
                location.visited = True
                self._handle_location_visit()
                return

        # Normal location visit handling
        print(location.get_description())
        location.visited = True

    def _display_available_actions(self) -> None:
        """Display available actions and commands to the player."""
        location = self.get_location()
        valid_items = [item.name.lower() for item in self._items
                       if item.current_position == self.current_location_id]

        if isinstance(location, StoryEvent):
            print("Actions:")
            for action in location.available_commands:
                print("-", action)

        elif location.is_locked:
            print("At this location, you can only:")
            for action in location.available_commands:
                print("-", action)
        else:
            print("What to do? Choose from: look, inventory, score, undo, log, quit, time, objective, toggledebug")
            print("At this location, you can also:")
            for action in location.available_commands:
                print("-", action)

            if location.looked:  # Check if the player has looked around
                valid_items = [item.name.lower() for item in self._items
                               if item.current_position == self.current_location_id]
                if valid_items:
                    print("You can pick up:", ", ".join(valid_items))

    def _get_player_choice(self, valid_items: list[str]) -> str:
        """Get and validate player input."""
        location = self.get_location()
        menu = ["look", "inventory", "score", "undo", "log", "quit", "time", "objective", "toggledebug"]

        if isinstance(location, StoryEvent):
            # Only allow choices specific to the StoryEvent
            valid_commands = list(location.available_commands.keys())

        # Only allow non-movement commands when locked
        elif location.is_locked:
            valid_commands = list(location.available_commands.keys())
        else:
            # Allow full access to commands when the room is unlocked
            valid_commands = menu + list(location.available_commands.keys()) + \
                            [f"pick up {item}" for item in valid_items] + \
                            [f"drop {item}" for item in self._get_inventory_items()] + \
                            [f"use {item}" for item in self._get_inventory_items()]

        while True:
            choice = input("\nEnter action: ").lower().strip()
            if (choice in valid_commands or choice.startswith('tp ') or
                    choice.startswith('use ') or choice.startswith('drop ') or choice.startswith('examine ')):
                return choice
            print("Invalid option. Try again.")

    def _process_menu_command(self, choice: str, game: AdventureGame, game_log: EventList) -> None:
        """Handle menu commands that don't change location."""
        if choice == "look":
            self._handle_look_command(game)
        elif choice == "inventory":
            self._handle_inventory_command()
        elif choice == "score":
            self._handle_score_command()
        elif choice == "undo":
            self._handle_undo_command(game, game_log)
        elif choice == "log":
            game_log.display_events()
        elif choice == "quit":
            game.ongoing = False
            print("Quitting game...")
        elif choice == "time":
            self._handle_time_command()  # Add this line
        elif choice == "objective":
            print(f"Current Objective: {self.current_objective}")
        elif choice == "toggledebug":
            AdventureGame.debug_mode = not AdventureGame.debug_mode
            print(f"Debug mode {'enabled' if AdventureGame.debug_mode else 'disabled'}.")

    def _process_game_command(self, choice: str, game: AdventureGame, game_log: EventList) -> None:
        """Handle game commands that affect game state."""
        new_event = self._create_new_event(game)

        if choice.startswith("use "):
            self._handle_use_item(choice, game, new_event)
        elif choice.startswith("pick up "):
            self._handle_item_pickup(choice, game, new_event)
        elif choice.startswith("drop "):
            self._handle_item_drop(choice, game, new_event)
        elif choice.startswith("examine "):
            self._handle_examine_item(choice, game, new_event)
        elif choice.startswith("tp "):
            self._handle_teleport_command(choice)
            new_location = self.get_location()
            new_event.id_num = new_location.id_num
            if not new_location.visited:
                new_event.description = new_location.long_description
            else:
                new_event.description = new_location.brief_description
        elif choice == "password":
            self._handle_password_input(game)
        else:
            self._handle_movement(choice, game)

        game_log.add_event(new_event, choice)

        if AdventureGame.debug_mode:
            print(f"[DEBUG] Event logged: Location={new_event.id_num}, Command={choice}")
            game_log.display_events()

    # Additional helper functions
    def _get_inventory_items(self) -> list[str]:
        """Return list of item names in inventory."""
        return [item.name for item in self._items if item.current_position == -1]

    def _handle_look_command(self, game: AdventureGame) -> None:
        location = game.get_location()
        print(location.look_around())
        location.looked = True  # Mark that the player has looked around (in this location)

    def _handle_inventory_command(self) -> None:
        """Display inventory contents."""
        inventory = self._get_inventory_items()
        print("Inventory:", ", ".join(inventory) if inventory else "(empty)")

    def _handle_score_command(self) -> None:
        """Display current score."""
        # Implement actual scoring logic here
        print(f"Your score is {self.score} points.")

    def _handle_undo_command(self, game: AdventureGame, game_log: EventList) -> None:
        """Handle undo command."""
        last_event = game_log.remove_last_event()
        if last_event is None:
            print("Nothing to undo!")
            return

        if last_event.prev:
            game.current_location_id = last_event.prev.id_num
            print(f"Undo successful. Back to {game.get_location().name}.")

        if last_event.item_affected:
            item = next((i for i in self._items if i.name == last_event.item_affected), None)
            if item:
                item.current_position = last_event.item_prev_location
                location_name = "inventory" if last_event.item_prev_location == -1 \
                    else game.get_location(last_event.item_prev_location).name
                print(f"{item.name} returned to {location_name}.")

    def _create_new_event(self, game: AdventureGame) -> Event:
        """Create new event for logging."""
        location = game.get_location()
        return Event(
            id_num=location.id_num,
            description=location.long_description if not location.visited else location.brief_description,
            next_command=None,
            next=None,
            prev=None,
            item_affected=None,
            item_prev_location=None
        )

    def _handle_item_pickup(self, choice: str, game: AdventureGame, event: Event) -> None:
        """Handle item pickup logic."""
        item_name = choice.replace("pick up ", "").strip().lower()
        item = next((i for i in self._items if
                    i.name.lower() == item_name and i.start_position == game.current_location_id), None)

        if item:
            event.item_affected = item.name
            event.item_prev_location = item.start_position
            item.current_position = -1
            self.score += 10
            print(f"You picked up {item.name}! (+10 points)")
        else:
            print("There's no such item here.")

    def _handle_item_drop(self, choice: str, game: AdventureGame, event: Event) -> None:
        """Handle item drop logic."""
        item_name = choice.replace("drop ", "").strip().lower()
        item = next((i for i in self._items if i.name.lower() == item_name and i.current_position == -1), None)

        if item:
            event.item_affected = item.name
            event.item_prev_location = -1
            item.current_position = game.current_location_id
            print(f"You dropped {item.name}.")
        else:
            print("You don't have that item.")

    def _handle_use_item(self, choice: str, game: AdventureGame, event: Event) -> None:
        item_name = choice.replace("use ", "").strip().lower()
        item = next((i for i in self._items if i.name.lower() == item_name and i.current_position == -1), None)

        if item:
            current_location_id = self.current_location_id
            if item.use_location == current_location_id:
                print(f"You used the {item.name}.")

                if item.triggers_event_id:
                    self.current_location_id = item.triggers_event_id
            else:
                print(f"You can't use {item.name} here.")
        else:
            print("You don't have that item in your inventory.")

    def _handle_examine_item(self, choice: str, game: AdventureGame, event: Event) -> None:
        item_name = choice.replace("examine ", "").strip().lower()
        item = next((i for i in self._items if i.name.lower() == item_name and i.current_position == -1), None)
        print(f"{item.description}.")

    def _handle_teleport_command(self, choice: str) -> None:
        """Handle teleport command."""
        parts = choice.split()
        if len(parts) != 2:
            print("Invalid teleport command. Usage: tp <location_id>")
            return
        try:
            loc_id = int(parts[1])
        except ValueError:
            print("Invalid location ID. Must be an integer.")
            return

        try:
            self.get_location(loc_id)
            self.current_location_id = loc_id
            print(f"Teleported to location {loc_id}.")
        except KeyError:
            print("Invalid location ID. No such location exists.")

    def _handle_time_command(self) -> None:
        """Display the current in-game time."""
        hours = self.current_time // 60
        minutes = self.current_time % 60
        print(f"Current time: {hours:02}:{minutes:02}")

    def _handle_password_input(self, game: AdventureGame) -> None:
        """Handle password input for puzzle locations."""
        current_location = game.get_location()

        if isinstance(current_location, Puzzle):
            password_attempt = input("Enter the password: ").strip().lower()
            if password_attempt in current_location.answers:
                print("Correct password! You can now proceed.")
                # Move to the next location after solving the puzzle
                next_location_id = list(current_location.available_commands.values())[0]
                self.current_location_id = next_location_id
                print(f"You move to {self.get_location(next_location_id).name}.")
            else:
                print("Incorrect password. Try again.")
        else:
            print("There's no password to enter here.")

if __name__ == "__main__":
    game_log = EventList()
    game = AdventureGame('game_data.json', 1) #Insert starting ID here :D
    menu = ["look", "inventory", "score", "undo", "log", "quit", "time", "objective", "toggledebug"]

    while game.ongoing:
        # Handle location visit logic
        game._handle_location_visit()

        # Get valid items for current location
        valid_items = [item.name.lower() for item in game._items
                      if item.current_position == game.current_location_id]

        # Debug information
        if AdventureGame.debug_mode:
            print(f"[DEBUG] Current location: {game.current_location_id}")
            print(f"[DEBUG] Items here: {[item.name for item in game._items 
                                      if item.current_position == game.current_location_id]}")

        # Display actions
        game._display_available_actions()

        # Get player input
        choice = game._get_player_choice(valid_items)
        print("========")
        print("You decided to:", choice)

        # Process command
        if choice in menu:
            game._process_menu_command(choice, game, game_log)
        else:
            game._process_game_command(choice, game, game_log)
