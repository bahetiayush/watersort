from typing import List, Optional, Any, Dict, Tuple


TOTAL_COLORS = {
    "RED",
    "LIGHT_GREEN",
    "BLUE",
    "LIGHT_BLUE",
    "GREY",
    "ORANGE",
    "BROWN",
    "MEHENDI",
    "PINK",
    "PURPLE",
    "YELLOW",
    "GREEN",
    None,
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
        self.valid_tube()

    def __repr__(self) -> str:
        """Returns the name of the tube."""
        return self.name

    def filled_slots(self) -> int:
        """Returns the number of filled slots in the tube."""
        return sum(1 for color in self.colors if color is not None)

    def empty_slots(self) -> int:
        """Returns the number of empty slots in the tube."""
        return 4 - self.filled_slots()

    def completed_tube(self) -> bool:
        """Returns True if the tube is completed (all 4 slots filled with the same color)."""
        filled_colors = [color for color in self.colors if color is not None]
        return len(filled_colors) == 4 and len(set(filled_colors)) == 1

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
