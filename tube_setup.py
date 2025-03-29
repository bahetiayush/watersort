from typing import List, Optional, Any, Dict, Tuple


TOTAL_COLORS = {
    "RED",
    "LIGHT_GREEN",
    "BLUE",
    "LIGHT_BLUE",
    "GREY",
    "ORANGE",
    "BROWN",
    "LIME_GREEN",
    "PINK",
    "PURPLE",
    "YELLOW",
    "DARK_GREEN",
    None,
}

COLORS_WITH_HEX = {
  "BROWN": "#7f4a08",
  "LIGHT_GREEN": "#61d67d",
  "BLUE": "#3b2fc3",
  "GREY": "#636466",
  "DARK_GREEN": "#116533",
  "RED": "#ff0000",
  "PINK": "#ea5e7b",
  "LIME_GREEN": "#78970e",
  "LIGHT_BLUE": "#55a3e5",
  "ORANGE": "#e88c41",
  "PURPLE": "#722b95",
  "YELLOW": "#f2d958",
  "NONE": "#f5f5f5"
}


class Tube:
    """Represents a single tube in the water sort puzzle."""

    def __init__(self, colors: List[Optional[str]], name: str) -> None:
        """
        Initializes a Tube object.

        Args:
            colors: A list of colors (strings) in the tube, from bottom to top.
                    Empty slots are represented by None.
            name: A string identifier for the tube.
        Raises:
            ValueError: if the tube does not have 4 colors
        """
        self.name = name
        self.colors = colors if colors else [None] * 4
        self.max_slots = 4
        self.valid_tube()


    def __repr__(self) -> str:
        """Returns the name of the tube."""
        return self.name

    
    def is_empty(self) -> bool:
        """Checks if the tube is empty."""
        return self.filled_slots() == 0

    def is_full(self) -> bool:
        """Checks if the tube is full."""
        return self.filled_slots() == self.max_slots
    
    def is_bottom(self, color):
        """checks if the color is at the bottom"""
        return self.colors[0] == color

    def completed_tube(self) -> bool:
        """Returns True if the tube is completed (all 4 slots filled with the same color)."""
        if self.is_empty():
            return False
        first_color = None
        for color in self.colors:
            if first_color is None:
                first_color = color
            if color != first_color:
                return False
        return True

    def empty_tube(self) -> bool:
        """Returns True if the tube is empty."""
        return all(color is None for color in self.colors)

    def tube_details(self) -> Tuple[Optional[str], int, int]:
        """
        Returns details about the tube's top color and filled slots.

        Returns:
            A tuple containing:
            - top_color: The color of the topmost block (or None if empty).
            - top_color_count: The number of consecutive blocks of the top color.
            - filled_slots: The total number of filled slots.
        """
        filled_colors = [color for color in self.colors if color is not None]
        filled_slots = len(filled_colors)

        if not filled_slots:
            return None, 0, 0

        top_color = filled_colors[-1]
        top_color_count = 1
        index = filled_slots - 2

        while index >= 0 and filled_colors[index] == top_color:
            top_color_count += 1
            index -= 1

        return top_color, top_color_count, filled_slots

    def valid_tube(self) -> None:
        """
        Validates the current tube

        Raises:
            ValueError: if the tube does not have 4 colors
            ValueError: if there are empty colors in the middle
            ValueError: if the colors are invalid.
        """
        if len(self.colors) != 4:
            raise ValueError("A tube MUST have 4 slots")
        if None in self.colors:
            index: int = self.colors.index(None)
            remaining_tube: List[Optional[str]] = self.colors[index:]
            if any(remaining_tube):
                raise ValueError("Empty slots in the middle are not allowed")
            colored_tube: List[Optional[str]] = self.colors[: index ]
            check_colors(colored_tube)
        else:
            check_colors(self.colors)

    def add_color(self, color: str):
        """Adds a color to the tube."""
        if self.is_full():
            raise ValueError("Tube is full")
        self.colors.append(color)
        #Automatic update handled by getter methods


    def remove_color(self):
        """Removes a color from the tube."""
        if self.is_empty():
            raise ValueError("Tube is empty")
        color = self.colors.pop()
        #Automatic update handled by getter methods
        return color

    def get_color_to_move(self) -> Optional[str]:
        """Gets the color that should be moved from the top."""
        for color in reversed(self.colors):
            if color is not None:
                return color
        return None

    def filled_slots(self) -> int:
        """Returns the number of filled slots."""
        return sum(1 for color in self.colors if color is not None)

    def empty_slots(self) -> int:
        """Returns the number of empty slots."""
        return self.max_slots - self.filled_slots()



def check_colors(colors: list) -> None:
    """
    Validates if the current list of colors are correct.

    Args:
        colors: List of colors
    Raises:
        ValueError: if the colors are not valid.
    """
    if not all(element in TOTAL_COLORS for element in colors):
        raise ValueError("Tube has undefined colours")


def tube_to_dict(tube: Tube) -> Dict[str, Any]:
    """Converts a Tube object to a dictionary for JSON serialization."""
    return {"name": tube.name, "colors": tube.colors}


def tubes_list_to_dict(tubes: List[Tube]) -> List[Dict[str, Any]]:
    """Converts a list of Tube objects to a list of dictionaries."""
    return [tube_to_dict(tube) for tube in tubes]

class Movement:
    """Represents a single move between two tubes."""

    def __init__(self, from_tube: Tube, to_tube: Tube):
        """Initializes a Movement object."""
        self.from_tube: Tube = from_tube
        self.to_tube: Tube = to_tube

    def __repr__(self) -> str:
        """Returns a string representation of the move."""
        return f"Move from {self.from_tube} to {self.to_tube}"

    def __eq__(self, other: object) -> bool:
        """Checks if two Movement objects are equal."""
        if not isinstance(other, Movement):
            return False
        return self.from_tube == other.from_tube and self.to_tube == other.to_tube

    def execute(self) -> None:
        """Performs a movement of water from one tube to another."""
        if not self.is_possible():
            return

        from_tube_top_color, from_tube_top_color_slots, from_tube_filled_slots = self.from_tube.tube_details()
        to_tube_filled_slots: int = self.to_tube.filled_slots()

        self.to_tube.colors[to_tube_filled_slots: to_tube_filled_slots + from_tube_top_color_slots] = [
            from_tube_top_color
        ] * from_tube_top_color_slots
        self.from_tube.colors[
            from_tube_filled_slots - from_tube_top_color_slots: from_tube_filled_slots
        ] = [None] * from_tube_top_color_slots
        # Explicitly update tubes after modification
        self.from_tube.valid_tube()
        self.to_tube.valid_tube()

    def is_possible(self) -> bool:
        """
        Checks if a movement is possible between two tubes.

        Returns:
            True if a movement is possible, False otherwise.
        """
        if self.from_tube == self.to_tube:
            return False
        if self.from_tube.tube_details()[0] is None:
            return False

        from_tube_top_color, from_tube_top_color_slots, from_tube_filled_slots = self.from_tube.tube_details()
        to_tube_top_color, to_tube_top_color_slots, to_tube_filled_slots = self.to_tube.tube_details()
        to_tube_empty_slots: int = self.to_tube.empty_slots()

        if from_tube_filled_slots == from_tube_top_color_slots and to_tube_filled_slots == 0:
            return False
        if from_tube_top_color_slots > to_tube_empty_slots:
            return False
        if to_tube_top_color not in [from_tube_top_color, None]:
            return False

        return True

