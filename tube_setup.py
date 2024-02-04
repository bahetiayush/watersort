
total_colors = {
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
    None
}


class Tube:
    def __init__(self, colors: list, name: str):
        self.name = name
        self.colors = colors if colors else [None] * 4
        self.valid_tube()

    def __repr__(self):
        return self.name

    def filled_slots(self):
        filled_colors = [color for color in self.colors if color is not None]
        filled_slots = len(filled_colors)
        return filled_slots
    
    def empty_slots(self):
        filled_colors = [color for color in self.colors if color is not None]
        filled_slots = len(filled_colors)
        empty_slots = len(self.colors) - filled_slots
        return empty_slots
    
    def completed_tube(self):
        filled_colors = [color for color in self.colors if color is not None]
        if len(filled_colors) == 4 and len(set(filled_colors)) == 1:
            return True
        else:
            return False
    
    def empty_tube(self):
        filled_colors = [color for color in self.colors if color is not None]
        if filled_colors == []:
            return True
        else:
            return False

    def tube_details(self):
        filled_colors = [color for color in self.colors if color is not None]
        filled_slots = len(filled_colors)

        top_color = None
        top_color_count = 0

        if filled_slots > 0:
            top_color = filled_colors[-1]
            top_color_count = 1

            for index in range(filled_slots - 2, -1, -1):
                if filled_colors[index] == top_color:
                    top_color_count += 1
                else:
                    break

        return top_color, top_color_count, filled_slots
    
    
    def valid_tube(self):
        if len(self.colors) != 4:
            raise ValueError("A tube MUST have 4 slots")
        else:
            if None in self.colors:
                index = self.colors.index(None)
                remaining_tube = self.colors[index:]
                if any(remaining_tube) != 0:
                    raise ValueError("Empty slots in the middle are not allowed")
                else:
                    colored_tube = self.colors[0:index-1]
                    valid = check_colors(colored_tube)                    
                    return valid
            else:
                valid = check_colors(self.colors)
                return valid
            

def check_colors(colors: list):
    if all([element in total_colors for element in colors]):
        return True
    else:
        raise ValueError("Tube has undefined colours")
