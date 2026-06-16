from .options import Options, Option
from scr.screen import Screen
from scr.config import Config
import curses
import os
import sys

class CursesDisplay():
    def __init__(self, config=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self.style = "Curses"
        self.enter_new = False
        self.new_screen = ""
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


    def __str__(self):
        return self.style
    def __repr__(self):
        return "<class 'CursesDisplay'>"



    def draw_menu(self, stdscr, current_row):
        """
          Draw the menu with the current selection highlighted
        """
        mitm = "{menu_char}) {text}" # menu line format
        stdscr.clear()
        menu_max_w = max(
           [len(
             mitm.format(menu_char=i.menu_char,
                         text=i.text)) for i in self.menu_options])
        h, w = stdscr.getmaxyx()
        menu_len = self.menu_options.length
        if h-5 < menu_len:
            curses.endwin()
            self.log.error("Screen list longer than available height.\n"+\
                           "Use -t/--text, reduce number of screen "+\
                           "sessions, or increase display height to "+\
                           "use curses display.\n"+\
                           f"Available Screen Height    : {h-5}\n"+\
                           f"Screen Session list length : {menu_len}")
            sys.exit(1)

        # Draw title
        title = self.menu_title
        stdscr.addstr(0, w//2 - len(title)//2, title, curses.A_BOLD)
        stdscr.addstr(1, w//2 - len(title)//2, "=" * len(title))

        # Draw menu items
        for idx, item in enumerate(self.menu_options, start=1):
            x = w//2 - menu_max_w//2
            #x = w//2 - len(str(item))//2
            y = h//2 - self.menu_options.length//2 + idx-1
            item_text = mitm.format(menu_char=item.menu_char, text=item.text)
            if idx == current_row and not self.enter_new:
                # Highlight selected item
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, item_text)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, item_text)
        # Draw New Screen name entry area if needed
        if self.enter_new:
            scr_name = "<EMPTY>" if self.new_screen == "" else self.new_screen
            prompt=f"New Screen Name: {scr_name: <25}"
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(h-3,w//2 - len(prompt)//2, prompt)
            stdscr.attroff(curses.color_pair(1))
            instructions = "Type a new Screen Name, Enter to accept. "+\
                           "<ESC> to go Back"
        else:
            instructions =  "Use ↑/↓ to navigate, Enter to select, "+\
                            "'N' for New Screen, '<ESC>' to Exit"
        # Draw instructions
        stdscr.addstr(h-2, w//2 - len(instructions)//2,
                      instructions, curses.A_DIM)
        stdscr.refresh()



    def input_loop(self, stdscr):
        """Main menu loop"""
        # Initialize colors
        curses.curs_set(0)  # Hide cursor

        # Only initialize color pair if colors are supported
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        current_row = 1
        menu_length = self.menu_options.length
        while True:
            self.draw_menu(stdscr, current_row)

            # Get user input
            key = stdscr.getch()
            if self.enter_new and not key == ord('\n'):
               c = chr(key)
               if key in [curses.KEY_BACKSPACE,8,127,curses.KEY_DC]:
                   self.new_screen = self.new_screen[:-1]
                   continue
               elif key == 27:
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
                #elif key == ord('e') or key == ord('E'):
            elif key == 27:
                stdscr.clear()
                curses.endwin()
                return False
                break
            elif key == ord('n') or key == ord('N'):
                self.enter_new = True
            if key == ord('\n'):  # Enter key
                stdscr.clear()
                curses.endwin()
                if self.enter_new:
                    if self.new_screen =="":
                        self.enter_new = False
                        continue
                    return Option("new",Screen(self.new_screen),"N")
                return list(self.menu_options)[current_row-1]

    def menu(self):
        # Set TERM environment variable if not set
        os.environ.setdefault('ESCDELAY','25')
        if 'TERM' not in os.environ:
            os.environ['TERM'] = 'xterm-256color'

        try:
            ret = curses.wrapper(self.input_loop)
            if ret:
                ret.action.run()
                sys.exit()
        except curses.error as e:
            print(f"\nError: {e}")
            print("This script requires a proper terminal environment.")









