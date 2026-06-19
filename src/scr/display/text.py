from .options import Options, Option
from scr.screen import Screen
from scr.config import Config
import sys

class TextDisplay():
    def __init__(self, config=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self.style = "text"
        self._menu = {
                       'title':None,
                       'options':Options(),
                       'controls':Options(allow_duplicates=False)
                     }
        self.menu_controls = [
                          Option('New Screen Session',None,"N"),
                          Option('Refresh Menu',None,'R'),
                          Option('EXIT',None,'E')
                         ]
        self._colors = {
                        "menu_color"   :self.config.get_text_color(
                                            self.config.menu_color),
                        "title_color"  :self.config.get_text_color(
                                            self.config.title_color),
                        "control_color":self.config.get_text_color(
                                            self.config.control_color),
                       }

    @property
    def menu_title(self):
        return self._menu['title']
    @menu_title.setter
    def menu_title(self,t):
        if isinstance(t, str):
            self._menu['title'] = t
            return
        raise TypeError("TextDisplay title must be of type 'str'")

    @property
    def menu_options(self):
        return self._menu['options']
    @menu_options.setter
    def menu_options(self,opts):
        self._menu['options']=Options(opts)
    @property
    def menu_controls(self):
        return self._menu['controls']
    @menu_controls.setter
    def menu_controls(self,opts):
        self._menu['controls']=Options(opts, allow_duplicates=False)

    @property
    def option(self):
        return Option
    @property
    def control(self):
        return Option.control
    @property
    def menu_color(self):
        return self._colors['menu_color']
    @property
    def title_color(self):
        return self._colors['title_color']
    @property
    def control_color(self):
        return self._colors['control_color']

    def __str__(self):
        return self.style
    def __repr__(self):
        return "<class 'TextDisplay'>"

    def get_string(self):
        new_name = input("New Screen Name: ")
        return new_name.replace(' ','_')

    def menu(self):
        self.display_menu()
        while True:
            choice = self.get_choice().lower()
            if choice == "e":
                sys.exit(0)
            elif choice == 'r':
                self.display_menu()
            elif choice == 'n': # create a new screen
                new_name = self.get_string()
                if not all(c.isalpha() or c =='_' for c in new_name):
                    log.error("[[R]]Screen can only be letters or _ [[E]]")
                    continue
                if not new_name:
                    log.error("[[R]]Empty screen name not allowed.[[E]]\n")
                    continue
                else:
                    new_screen = Screen(name=new_name)
                    new_screen.run()
            try:
                ch = int(choice)
            except:
                continue
            if ch not in [c.menu_char for c in self.menu_options]:
                continue
            else:
                [c.action for c in self.menu_options if ch==c.menu_char][0].run()


    def display_menu(self):
        self._display_title()
        self._display_menu_choices()

    def get_choice(self):
        return input(f"{self._menu_prompt} ?: ")

    def _display_title(self):
        filler = f"{'':─>{len(self.menu_title)}}"
        self.log(f"   ┌─{filler}─┐")
        self.log(f"   │ {self.title_color}{self.menu_title}[[E]] │")
        self.log(f"   └─{filler}─┘")

    def _display_menu_choices(self):
        for i,opt in enumerate(self.menu_options, start=1):
            self.log(f"{self.menu_color}{i}[[E]]) {self.menu_color}{opt}[[E]]")
        for ctl in self.menu_controls:
            self.log(f"{self.control_color}{ctl.menu_char}[[E]]) "+\
                     f"[ {self.control_color}{ctl}[[E]] ]")

    @property
    def _menu_prompt(self):
        choices = ""
        nopts = self.menu_options.length
        if nopts == 1:
            choices=(f"{self.menu_color}{nopts}[[E]]")
        elif nopts == 0:
            pass
        else:
            choices=(f"{self.menu_color}1-{nopts}[[E]]")
        if  self.menu_controls:
            ctls=f"{self.control_color}"+\
                 f"{','.join([c.menu_char for c in self.menu_controls])}[[E]]"
        return self.log.encodeColor(
               f"Choices [{','.join([choices,ctls])}]")




