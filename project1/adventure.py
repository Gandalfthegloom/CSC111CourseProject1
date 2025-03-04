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
from typing import ClassVar, Dict, List, Optional

from game_entities import Location, Item, StoryEvent, Puzzle, inquire
from proj1_event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - current_time:
            The current in-game time measured in minutes from midnight.
            The game starts at 14*60 minutes (i.e. 2:00 PM).
        - score:
            The player's current score.
        - current_objective:
            A textual description of the player's current objective.
        - current_location_id:
            The ID of the location where the player is currently situated.
        - ongoing:
            A Boolean indicating whether the game is still active.

    Representation Invariants:
        - current_time >= 0.
        - score >= 0.
        - current_location_id is in _locations_all.
        - (item.current_position == -1 or item.current_position in _locations_all for item in _items.)
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.
    #   - _locations_all: a dictionary of all locations and location subclasses (Story Event and Puzzle).
    #                     Originally separated but merged to prevent Python TA error.

    debug_mode: ClassVar[bool] = False
    _locations: dict[int, Location]
    _items: list[Item]
    _locations_all: dict[int, Location | StoryEvent | Puzzle]
    current_time: int
    score: int
    current_objective: str
    current_location_id: int
    ongoing: bool

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

        locations, items, stories, puzzles = self._load_game_data(game_data_file)
        self._items = items
        self._locations_all = {**locations, **stories, **puzzles}

        # Initialize to 2:00 PM (15*60 minutes)
        self.current_time = 14 * 60

        # Initialize score to 0
        self.score = 0

        # Set current player objective
        self.current_objective = "Find your missing project items before 4 PM."

        self.current_location_id = initial_location_id  # game begins at this location
        self.ongoing = True  # whether the game is ongoing

    @staticmethod
    def _load_game_data(filename: str) -> tuple[Dict[int, Location], List[str]]:
        """Load locations and items from a JSON file and return structured game data."""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)  # Load JSON data

        locations = {}
        for loc_data in data['locations']:
            locations[loc_data['id']] = Location(
                id_num=loc_data['id'],
                name=loc_data['name'],
                brief_description=loc_data.get('brief_description', ""),
                long_description=loc_data.get('long_description', ""),
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
                new_objective=story_data.get('new_objective', None),
                trigger_condition=story_data.get('trigger_condition', None)
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

    def get_current_location_items(self) -> list[Item]:
        """Method for access to _items, to prevent accessing private items."""
        return [item for item in self._items if item.current_position == self.current_location_id]

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """
        if loc_id is None:
            loc_id = self.current_location_id
        if loc_id in self._locations_all:
            return self._locations_all[loc_id]
        else:
            raise KeyError(f"Location ID {loc_id} not found in locations")

    def move(self, direction: str) -> bool:
        """
        Handles in-game movement, including checking for first visit event triggers,
        locked locations, puzzle movements, and time tracking.
        """
        current_location = self.get_location()

        if direction not in current_location.available_commands:
            print("You can't go that way.")
            return False

        new_location_id = current_location.available_commands[direction]
        new_location = self.get_location(new_location_id)

        # Check if the new location is locked
        if new_location.is_locked:
            if self.evaluate_unlock_condition(new_location.unlock_condition):
                new_location.is_locked = False
                print(f"You've unlocked {new_location.name}!")
            else:
                print(
                    f"{new_location.name} is locked. {'You need to fulfill the unlock condition.'}")

        # Handle Puzzle-specific movement
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
            # Update game time for regular locations
            if not isinstance(new_location, StoryEvent):
                self.current_time += 1

            # Check for game over due to time
            if self.current_time >= 16 * 60:
                print("\nYou've run out of time! It's now past 4:00 PM. Game Over.")
                print(f"Score: {self.score}")
                self.handle_time_command()
                self.ongoing = False
                return False

            new_location_id = current_location.available_commands[direction]
            self.current_location_id = new_location_id
            if not isinstance(current_location, StoryEvent):
                print(f"You move to {self.get_location().name}.")
            return True

    def evaluate_unlock_condition(self, condition: Optional[str]) -> bool:
        """Evaluate if the unlock condition is met."""
        if not condition:
            return False

        inventory = [item.name.lower() for item in self._items if item.current_position == -1]
        return eval(condition, {}, {"inventory": inventory})

    def handle_movement(self, choice: str, game: AdventureGame) -> None:
        """Handle movement between locations."""
        if choice in game.get_location().available_commands:
            game.move(choice)
        else:
            print("Invalid movement command.")

    def handle_location_visit(self, game_log: EventList) -> None:
        """Handle visiting a location or triggering a story event."""
        location = self.get_location()

        # If StoryEvent, display story content and give out items if available.
        if isinstance(location, StoryEvent):
            print(location.get_description())
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
                print(f"Score: {self.score}")
                self.handle_time_command()
                return

            if location.name == "Victory":
                self.score += 100
                self.ongoing = False
                print("You pass the torch onwards. Or maybe bacwards?")
                print(f"Score: {self.score}")
                self.handle_time_command()
                return

        # For regular locations, check if visited. hasattr just in case forgot to initiate lel
        if hasattr(location, 'visited'):
            if not location.visited:
                # Check for a first-time event trigger.
                if location.first_time_event_id:
                    self.current_location_id = location.first_time_event_id
                    self.handle_location_visit(game_log)
                    location.visited = True
                    return
                else:
                    # No first-time event to trigger, so display the description,
                    # award 5 bonus points, and mark the location as visited.
                    print(location.get_description())
                    self.score += 5
                    location.visited = True
                    return
            else:
                if self.ongoing:
                    print(location.get_description())

    def display_available_actions(self) -> None:
        """Display available actions and commands to the player.
            Available commands can include location-specific commands, menu commands, and game commands.
        """
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

    def get_player_choice(self, valid_items: list[str]) -> str:
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
            if (choice in valid_commands
                    or choice.startswith('tp ')
                    or choice.startswith('use ')
                    or choice.startswith('drop ')
                    or choice.startswith('examine ')):
                return choice
            print("Invalid option. Try again.")

    def process_menu_command(self, choice: str, game: AdventureGame, game_log: EventList) -> None:
        """Handle menu commands that don't change location.
        One of two main commands with process_game_command.
        """
        if choice == "undo":
            self.handle_undo_command(game_log)
            # Return immediately so that no "undo" event is logged.
            return

        new_event = self.create_new_event()

        if choice == "look":
            self.handle_look_command(game)
        elif choice == "inventory":
            self.handle_inventory_command()
        elif choice == "score":
            self.handle_score_command()
        elif choice == "log":
            game_log.display_events()
        elif choice == "quit":
            game.ongoing = False
            game_log.display_events()
            print("Quitting game...")
            return
        elif choice == "time":
            self.handle_time_command()
        elif choice == "objective":
            print(f"Current Objective: {self.current_objective}")
        elif choice == "toggledebug":
            AdventureGame.debug_mode = not AdventureGame.debug_mode
            print(f"Debug mode {'enabled' if AdventureGame.debug_mode else 'disabled'}.")

        game_log.add_event(new_event, choice)

    def process_game_command(self, choice: str, game: AdventureGame, game_log: EventList) -> None:
        """Handle game commands that affect game state.
        One of two main commands with process_game_command.
        """
        new_event = self.create_new_event()

        if (choice.startswith("use ") or choice.startswith("pick up ")
                or choice.startswith("drop ") or choice.startswith("examine ")):
            self.process_game_command_extra(choice, game, game_log)
        elif choice.startswith("tp "):
            self.handle_teleport_command(choice)
            new_location = self.get_location()
            new_event.id_num = new_location.id_num
            if not new_location.visited:
                new_event.description = new_location.long_description
            else:
                new_event.description = new_location.brief_description
        elif choice == "password":
            password_cmd_event = self.create_new_event()
            game_log.add_event(password_cmd_event, "password")
            password_answer = self.handle_password_input(game)
            if password_answer is not None:
                # Log the answer as a separate event.
                answer_event = self.create_new_event()
                game_log.add_event(answer_event, password_answer)
        elif choice == "book search":
            book_attempt = self.handle_book_search(game)
            if book_attempt is not None:
                # Add password event
                new_event = self.create_new_event()
                new_event.next_command = {book_attempt}
                game_log.add_event(new_event, choice)
                # Log the password and make new event
                game_log.add_event(new_event, book_attempt)
                return
        elif choice == "inquire":
            inquire()
        else:
            self.handle_movement(choice, game)

        new_event.id_num = self.current_location_id

        game_log.add_event(new_event, choice)

        if AdventureGame.debug_mode:
            print(f"[DEBUG] Event logged: Location={new_event.id_num}, Command={choice}")
            game_log.display_events()

    def process_game_command_extra(self, choice: str, game: AdventureGame, game_log: EventList) -> None:
        """Handle game commands that affect game state."""
        new_event = self.create_new_event()
        if choice.startswith("use "):
            self.handle_use_item(choice)
        elif choice.startswith("pick up "):
            self.handle_item_pickup(choice, game, new_event)
        elif choice.startswith("drop "):
            self.handle_item_drop(choice, game, new_event)
        else:
            self.handle_examine_item(choice)

        new_event.id_num = self.current_location_id

        game_log.add_event(new_event, choice)

        if AdventureGame.debug_mode:
            print(f"[DEBUG] Event logged: Location={new_event.id_num}, Command={choice}")
            game_log.display_events()

    # Additional helper functions
    def _get_inventory_items(self) -> list[str]:
        """Return list of item names in inventory."""
        return [item.name for item in self._items if item.current_position == -1]

    def handle_look_command(self, game: AdventureGame) -> None:
        """Prints extra_description if available and increments time by 1 minute."""
        location = game.get_location()
        print(location.look_around())
        location.looked = True  # Mark that the player has looked around (in this location)
        self.current_time += 1

    def handle_inventory_command(self) -> None:
        """Display inventory contents."""
        inventory = self._get_inventory_items()
        print("Inventory:", ", ".join(inventory) if inventory else "(empty)")

    def handle_score_command(self) -> None:
        """Display current score."""
        # Implement actual scoring logic here
        print(f"Your score is {self.score} points.")

    def handle_undo_command(self, game_log: EventList) -> None:
        """Undo the last action by reverting the game to a previous state."""
        last_event = game_log.remove_last_event()
        if last_event is None:
            print("Nothing to undo!")
            return

        # Retrieve the saved state.
        snapshot = last_event.state_snapshot

        # Restore main variables
        self.score = snapshot["score"]
        self.current_time = snapshot["current_time"]
        self.current_location_id = snapshot["current_location_id"]
        self.current_objective = snapshot["current_objective"]
        self.ongoing = snapshot["ongoing"]

    # Restore state for items, locations, stories, puzzles!!!
        for item in self._items:
            if item.name in snapshot["items"]:
                item.current_position = snapshot["items"][item.name]

        for loc_id, states in snapshot["locations_all"].items():
            if loc_id in self._locations_all:
                self._locations_all[loc_id].visited = states["visited"]
                self._locations_all[loc_id].looked = states["looked"]

        print(f"Undo successful. Reverted to previous state at {self.get_location().name}.")

    def create_new_event(self) -> Event:
        """Create new event for logging."""
        state_snapshot = {
            "score": self.score,
            "current_time": self.current_time,
            "current_location_id": self.current_location_id,
            "current_objective": self.current_objective,
            "ongoing": self.ongoing,
            "items": {item.name: item.current_position for item in self._items},
            "locations_all": {loc_id: {"visited": loc.visited, "looked": loc.looked}
                              for loc_id, loc in self._locations_all.items()},

        }

        location = self.get_location()
        return Event(
            id_num=location.id_num,
            description=(location.long_description if not location.visited else location.brief_description),
            next_command=None,
            next=None,
            prev=None,
            state_snapshot=state_snapshot
        )

    def handle_item_pickup(self, choice: str, game: AdventureGame, event: Event) -> None:
        """Handle item pickup logic."""
        item_name = choice.replace("pick up ", "").strip().lower()
        item = next((i for i in self._items if
                    i.name.lower() == item_name and i.current_position == game.current_location_id), None)

        if item:
            event.item_affected = item.name
            event.item_prev_location = item.current_position
            item.current_position = -1
            if item.start_position != -1:
                event.score_change = 10  # Track score gained from picking up the item (FIRST TIME ONLY)
                item.start_position = -1
                self.score += 10
                print(f"You picked up {item.name}! (+10 points)")
            else:
                print(f"You picked up {item.name}!")
        else:
            print("There's no such item here.")

    def handle_item_drop(self, choice: str, game: AdventureGame, event: Event) -> None:
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

    def handle_use_item(self, choice: str) -> None:
        """Checks whether item can be used in a location, and if so triggers item-related event."""
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

    def handle_examine_item(self, choice: str) -> None:
        """Prints item description"""
        item_name = choice.replace("examine ", "").strip().lower()
        item = next((i for i in self._items if i.name.lower() == item_name and i.current_position == -1), None)
        print(f"{item.description}.")

    def handle_teleport_command(self, choice: str) -> None:
        """
        Handle teleport command.
        """
        parts = choice.split()
        if len(parts) != 2:
            print("Invalid teleport command. Usage: tp <location_id>")
            return
        else:
            loc_id = int(parts[1])
            if self.get_location():
                self.get_location(loc_id)
                self.current_location_id = loc_id
                print(f"Teleported to location {loc_id}.")
            else:
                print("Invalid location ID. No such location exists.")

    def handle_time_command(self) -> None:
        """Display the current in-game time."""
        hours = self.current_time // 60
        minutes = self.current_time % 60
        print(f"Current time: {hours:02}:{minutes:02}")

    def handle_password_input(self, game: AdventureGame) -> Optional[str]:
        """Handle password input for puzzle locations."""
        current_location = game.get_location()

        if isinstance(current_location, Puzzle):
            password_attempt = input("Enter the password: ").strip().lower()
            if password_attempt in current_location.answers:
                print("Correct password! You can now proceed.")
                # Move to the next location after solving the puzzle
                next_location_id = list(current_location.available_commands.values())[0]
                self.current_location_id = next_location_id
                return password_attempt
            else:
                print("Incorrect password. Try again.")
        else:
            print("There's no password to enter here.")

    def handle_book_search(self, game: AdventureGame) -> Optional[str]:
        """Handle password input for puzzle locations."""
        current_location = game.get_location()

        if isinstance(current_location, Puzzle):
            book_attempt = input("Enter section to search: ").strip().lower()
            if book_attempt in current_location.answers:
                print("Correct! You can now proceed.")
                # Move to the next location after solving the puzzle
                next_location_id = list(current_location.available_commands.values())[0]
                self.current_location_id = next_location_id
                return book_attempt
            else:
                print("Incorrect section. Try again.")
        else:
            print("There's no password to enter here.")

    def check_trigger_conditions(self) -> None:
        """Check all story events for trigger conditions and activate if met."""
        inventory = [item.name for item in self._items if item.current_position == -1]  # Get items in inventory

        for event in self._locations_all.values():
            if isinstance(event, StoryEvent) and event.trigger_condition:
                if eval(event.trigger_condition, {}, {"inventory": inventory}):
                    print(f"\n--- Event Triggered: {event.name} ---")
                    print(event.get_description())
                    self.current_location_id = event.id_num  # Move player to event location
                    break


if __name__ == "__main__":

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })
    game_obj_log = EventList()
    game_obj = AdventureGame('game_data.json', 1)  # Insert starting ID here :D
    menu_list = ["look", "inventory", "score", "undo", "log", "quit", "time", "objective", "toggledebug"]

    while game_obj.ongoing:
        # Get valid items for current location
        items_valid = [item.name.lower() for item in game_obj.get_current_location_items()]

        # DEBUGMODE!!
        if AdventureGame.debug_mode:
            print(f"[DEBUG] Current location: {game_obj.current_location_id}")
            print(f"[DEBUG] Items here: {[item.name for item in game_obj.get_current_location_items()]}")

        # Display actions
        game_obj.display_available_actions()

        # Get player input
        choice_str = game_obj.get_player_choice(items_valid)
        print("========")
        print("You decided to:", choice_str)

        # Process command
        if choice_str in menu_list:
            game_obj.process_menu_command(choice_str, game_obj, game_obj_log)
        else:
            game_obj.process_game_command(choice_str, game_obj, game_obj_log)

        game_obj.check_trigger_conditions()

        game_obj.handle_location_visit(game_obj_log)
