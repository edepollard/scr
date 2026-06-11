from .options import Options, Option
from scr.config import Config

class TextDisplay():
    def __init__(self, config=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self.style = "TextDisplay"
        self._menu = {
                       'title':None,
                       'options':Options(),
                       'controls':Options(allow_duplicates=False)
                     }

    @property
    def menu_title(self):
        return self._menu['title']
    @menu_title.setter
    def menu_title(self,t):
        if isinstance(t, str):
            self._menu['title'] = t
            return
        raise TypeError("TextDisplay menu_item must be of type 'str'")

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

    def __str__(self):
        return self.style
    def __repr__(self):
        return "<class 'TextDisplay'>"

    def get_string(self):
        new_name = input("New Screen Name: ")
        return new_name.replace(' ','_')

    def display_menu(self):
        self._display_title()
        self._display_menu_choices()

    def get_choice(self):
        return input(f"{self._menu_prompt} ?: ")

    def _display_title(self):
        filler = f"{'':─>{len(self.menu_title)}}"
        self.log(f"   ┌─{filler}─┐")
        self.log(f"   │ [[C]]{self.menu_title}[[E]] │")
        self.log(f"   └─{filler}─┘")

    def _display_menu_choices(self):
        for i,opt in enumerate(self.menu_options, start=1):
            self.log(f"[[Y]]{i}[[E]]) [[G]]{opt}[[E]]")
        for ctl in self.menu_controls:
            self.log(f"[[Y]]{ctl.menu_char}[[E]]) [ [[P]]{ctl}[[E]] ]")

    @property
    def _menu_prompt(self):
        choices = []
        nopts = self.menu_options.length
        if nopts == 1:
            choices.append(f"{nopts}")
        elif nopts == 0:
            pass
        else:
            choices.append(f"1-{nopts}")
        if  self.menu_controls:
            choices.extend([c.menu_char for c in self.menu_controls])
        return self.log.encodeColor(f"Choices [[[Y]]{','.join(choices)}[[E]]]")




