from .text import TextDisplay
from .curses import CursesDisplay
from scr.config import Config


DEFAULT_TYPE="text"
DISPLAYS = {
            'text':TextDisplay,
            'curses':CursesDisplay,
           }



class ScrDisplay():
    def __init__(self, title=None,
                       options=[], controls=[],
                       style=DEFAULT_TYPE,
                       config=None):
        self._config = config if config else Config()
        self.display=DISPLAYS[style](config=self.config)
        self.title = str(title)
        self.options = options
        self.controls = controls

    @property
    def config(self):
        return self._config
    @property
    def log(self):
        return self.config.log

    @property
    def options(self):
        return self.display.menu_options
    @options.setter
    def options(self, items):
        self.display.menu_options = items

    @property
    def controls(self):
        return self.display.menu_controls
    @controls.setter
    def controls(self, items):
        self.display.menu_controls = items

    @property
    def title(self):
        return self.display.menu_title
    @title.setter
    def title(self, text):
        if isinstance(text, str):
            self.display.menu_title = text
        else:
            raise TypeError(f"<ScrDisplay> title must be of type 'str'")

    def __str__(self):
        opts = f"options:{self.options}"
        ctls = f"options:{self.controls}"
        ttl =  f"title:'{self.title}'"
        style =f"style: {self.display}"
        return f"ScrDisplay: {ttl} {opts} {ctls} {style}"
    def __repr__(self):
        return f"<ScrDisplay> title:'{self.title}' options:{self.options}>"

    def addMenuOption(self, text, action, ctl_char):
        self.options.add(
              self.display.option(text,action, ctl_char))

    def addMenuControl(self, text, action, ctl_char):
        self.controls.add(
              self.display.control(text,action,ctl_char))

    def getMenuChoice(self):
        return self.log.encodeColor(self.display.get_choice()).strip()

    def getString(self):
        return self.display.get_string()

    def showMenu(self):
        self.display.display_menu()





