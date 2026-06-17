from .options import Options, Option
from scr.screen import Screen
from scr.config import Config
import curses
import os
import sys

BLACK = curses.COLOR_BLACK
WHITE = curses.COLOR_WHITE
CYAN = curses.COLOR_CYAN
GREEN = curses.COLOR_GREEN
MAGENTA = curses.COLOR_MAGENTA
YELLOW = curses.COLOR_YELLOW

class CursesDisplay():
    def __init__(self, config=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self.style = "Curses"
        self.enter_new = False
        self.new_screen = ""
        self._stdscr = False
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
        raise TypeError("CursesDisplay title must be of type 'str'")

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
    def stdscr(self):
        return self._stdscr
    @stdscr.setter
    def stdscr(self, s):
        self._stdscr = s

    def __str__(self):
        return self.style
    def __repr__(self):
        return "<class 'CursesDisplay'>"

    def _init_colors(self):
        colors={
                'highlight' : self._init_color(1, BLACK, WHITE),
                'cyan'      : self._init_color(2, CYAN, BLACK),
                'green'     : self._init_color(3, GREEN, BLACK),
                'magenta'   : self._init_color(4, MAGENTA, BLACK),
                'yellow'    : self._init_color(5, YELLOW, BLACK),
               }
        self.MENU_COLOR = colors[self.config.menu_color]
        self.TITLE_COLOR = colors[self.config.title_color]
        self.CONTROL_COLOR = colors[self.config.control_color]

    def _init_color(self, index, foreground, background):
        curses.init_pair(index,foreground,background)
        return curses.color_pair(index)

    def _addcolorstr(self, color, *args, **kwargs):
        if self.config.color:
            self.stdscr.attron(color)
        self.stdscr.addstr(*args, **kwargs)
        if self.config.color:
            self.stdscr.attroff(color)

    def _exit_menu_too_long(self, maxh, menu_len):
        if maxh >= menu_len:
            return
        curses.endwin()
        self.log.error("Screen list longer than available height.\n"+\
                       "Use -t/--text, reduce number of screen "+\
                       "sessions, or increase display height to "+\
                       "use curses display.\n"+\
                       f"Available Screen Height    : {maxh}\n"+\
                       f"Screen Session list length : {menu_len}")
        sys.exit(1)

    def draw_menu(self, current_row):
        """
          Draw the menu with the current selection highlighted
        """
        #mitm = "{menu_char}) {text}" # menu line formata
        stdscr = self.stdscr
        stdscr.erase()
        menu_max_w = max([len(i.text) for i in self.menu_options])
        h, w = stdscr.getmaxyx()
        menu_len = self.menu_options.length
        self._exit_menu_too_long(h-5, menu_len)

        # Draw title
        title = self.menu_title
        self._addcolorstr(self.TITLE_COLOR, 0, w//2 - len(title)//2, title)
        stdscr.addstr(1, 0, "─" * w, curses.A_DIM)

        # Draw menu items
        for idx, item in enumerate(self.menu_options, start=1):
            x = w//2 - menu_max_w//2
            y = h//2 - self.menu_options.length//2 + idx-1
            blank=" "
            item_back = f"[{blank: <{menu_max_w}}]"
            stdscr.addstr(y, x-1, item_back, curses.A_DIM)
            item_text = f"{item.text: <{menu_max_w}}"
            if idx == current_row and not self.enter_new:
                # Highlight selected item
                stdscr.addstr(y, x, item_text, curses.A_REVERSE | curses.A_BOLD)
            else:
                self._addcolorstr(self.MENU_COLOR, y, x, item_text)
        # Draw New Screen name entry area if needed
        if self.enter_new:
            scr_name = "<EMPTY>" if self.new_screen == "" else self.new_screen
            prompt="New Screen Name: "
            name= f"{scr_name: <25}"
            self._addcolorstr(self.CONTROL_COLOR,
                              h-3,w//2 - (len(prompt)+12//2), prompt)
            stdscr.addstr(h-3,w//2 - (len(prompt)+12//2)+len(prompt),
                          name, curses.A_REVERSE)
            instructions = "Back: <ESC>  Type new Screen Name  Accept:<Enter>"
        else:
            instructions =  "Navigate:↑/↓  Select:<Enter>  "+\
                            "New Screen:<N>  Quit:<ESC>|<Q>"
        # Draw instructions
        stdscr.addstr(h-1, w//2 - len(instructions)//2,
                      instructions, curses.A_DIM)
        stdscr.addstr(h-2, 0, "─" * w, curses.A_DIM)
        stdscr.refresh()

    def input_loop(self, stdscr):
        """Main menu loop"""
        self.stdscr = stdscr
        # Initialize colors
        curses.curs_set(0)  # Hide cursor
        # Only initialize color pair if colors are supported
        if curses.has_colors():
            self._init_colors()

        current_row = 1
        menu_length = self.menu_options.length
        while True: # main menu draw loop
            self.draw_menu(current_row)
            # Get user input
            key = stdscr.getch()
            if key == ord('\n'):  # Enter key
                stdscr.clear()
                curses.endwin()
                if self.enter_new:
                    if self.new_screen =="":
                        self.enter_new = False
                        continue
                    return Option("new",Screen(self.new_screen),"N")
                return list(self.menu_options)[current_row-1]
            elif self.enter_new:
               c = chr(key)
               if key in [curses.KEY_BACKSPACE,8,127,curses.KEY_DC]:
                   self.new_screen = self.new_screen[:-1]
                   continue
               elif key == 27: # escape==27
                   self.new_screen = ""
                   self.enter_new=False
                   continue
               elif c.isalnum() or c in ['_','-']:
                   self.new_screen = f"{self.new_screen}{chr(key)}"
               continue
            elif key == curses.KEY_UP and current_row > 1:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < menu_length:
                current_row += 1
            elif key in [27, ord('q'), ord('Q')]: #escape==27
                curses.endwin()
                return False
            elif key in [ord('n'), ord('N')]:
                self.enter_new = True

    def menu(self):
        # Set TERM environment variable if not set
        os.environ.setdefault('ESCDELAY','25')
        if 'TERM' not in os.environ:
            os.environ['TERM'] = 'xterm-256color'
        try:
            ret = curses.wrapper(self.input_loop)
            if ret:
                curses.endwin()
                ret.action.run()
                sys.exit()
        except curses.error as e:
            print(f"\nError: {e}")
            print("This script requires a proper terminal environment.")









