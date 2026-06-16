from .display.text import TextDisplay
from .display.curses import CursesDisplay
from .screen import Screens, Screen
from .config import Config


DEFAULT_TYPE="text"
DISPLAYS = {
            'text':TextDisplay,
            'curses':CursesDisplay,
           }



class ScrDisplay():
    def __init__(self, title=None,
                       options=[], controls=[],
                       config=None):
        self._config = config if config else Config()
        self.display=DISPLAYS[self.style](config=self.config)
        self.title = str(title)
        self._screens = None
        self.options = options
        self.populateScreens()

    @property
    def config(self):
        return self._config
    @property
    def log(self):
        return self.config.log
    @property
    def style(self):
        return self.config.style
    @style.setter
    def style(self, s):
        self.config.style = s #let config handle the validation

    @property
    def screens(self):
        return self._screens
    @screens.setter
    def screens(self, item):
        if isinstance(item, Screens):
           self._screens = item
        else:
           raise TypeError("<ScrDisplay>.screens must an instance of <Screen>")

    @property
    def options(self):
        return self.display.menu_options
    @options.setter
    def options(self, items):
        self.display.menu_options = items

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

    def addMenuControl(self, text, action, ctl_char): # remove
        self.controls.add(
              self.display.control(text,action,ctl_char))

    def populateScreens(self):
        self.screens = Screens.with_defaults(config=self.config)
        for idx, screen in enumerate(self.screens, start=1):
            detail = ''
            if screen.is_active:
                detail = f"{screen.longName: <5} {screen.state: <5}"
            self.addMenuOption(f"{screen.name: <5} {detail: <5}", screen, idx)

    def getMenuChoice(self): # remove
        return self.log.encodeColor(self.display.get_choice()).strip()

    def getString(self): # remove
        return self.display.get_string()

    def menu(self):
        self.display.menu()





