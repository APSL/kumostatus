import matplotlib.colors
from pprint import pprint

class Metric(object):

    def __init__(self):
        self.color_counter = 0
        self.metrics = []
        self.colors = self._generate_colors()

    def _generate_colors(self):
        colors = ['blue', 'green', 'red', 'magenta', 'orange', 'black', 'brown', 'grey', 'olive']  # strong colors
        for color in matplotlib.colors.cnames.keys():
            if color not in colors and 'light' not in color:
                colors.append(color)
        return colors

    def add(self, s):
        s.color = self.get_next_color()

        if len(s.points) > 0:
            self.metrics.append(s)


    def get_next_color(self):
        if self.colors:
            return self.colors.pop(0)
