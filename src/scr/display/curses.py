from .options import Options
import curses

class CursesDisplay():
    def __init__(self):
        self.style = "Curses"
    def __str__(self):
        return self.style
    def __repr__(self):
        return "<class 'CursesDisplay'>"




