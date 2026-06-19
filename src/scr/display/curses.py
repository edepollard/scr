from .options import Options, Option
from scr.screen import Screen
from scr.config import Config
import curses
import os
import sys
from socket import gethostname
from getpass import getuser

BLACK = curses.COLOR_BLACK
WHITE = curses.COLOR_WHITE
CYAN = curses.COLOR_CYAN
GREEN = curses.COLOR_GREEN
MAGENTA = curses.COLOR_MAGENTA
YELLOW = curses.COLOR_YELLOW
RED = curses.COLOR_RED
BLUE = curses.COLOR_BLUE
DIM = curses.A_DIM
REV = curses.A_REVERSE

class YX():
    def __init__(self, y=0, x=0):
        self._y = 0
        self._x = 0
        if y: self.y = y
        if x: self.x = x

    def __str__(self):
        return f"y:{self.y}, x:{self.x}"
    def __repr__(self):
        return f"<YX y:{self.y}, x:{self.x}>"
    def __call__(self):
        return self.y, self.x

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,i):
        if not isinstance(i, int) or i < 0:
            raise TypeError("YX.y must be an int greater than -1.")
        self._y = i

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,i):
        if not isinstance(i, int) or i < 0:
            raise TypeError("YX.x must be an int greater than -1.")
        self._x = i


class CursesDisplay():
    def __init__(self, config=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self.style = "curses"
        self.new_screen = ""
        self._stdscr = False
        self._h = 0
        self._w = 0
        self.current_row = 1
        self._menu_max_w = None
        self._menu_len = False
        self.mode = 'menu'
        self.r_arrow = "➤"
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
    def menu_max_w(self):
        if not self._menu_max_w:
            self._menu_max_w = max([len(i.text) for i in self.menu_options])
        return self._menu_max_w

    @property
    def menu_len(self):
        if not self._menu_len:
            self._menu_len = self.menu_options.length
        return self._menu_len

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

    @property
    def h(self):
        return self._h
    @h.setter
    def h(self, i):
        if not isinstance(i, int):
            raise TypeError("<ScrMenu>.h must be of type 'int'>")
        self._h = i

    @property
    def w(self):
        return self._w
    @w.setter
    def w(self, i):
        if not isinstance(i, int):
            raise TypeError("<ScrMenu>.w must be of type 'int'>")
        self._w = i

    @property
    def hostname(self):
        return gethostname().split('.')[0]

    @property
    def username(self):
        return getuser()

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
                'red'       : self._init_color(6, RED, BLACK),
                'blue'      : self._init_color(7, BLUE, BLACK),
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

    def _addcolorstrs(self, color, strs=[]):
        for s in strs:
            self._addcolorstr(color, s[0], s[1], s[2])

    def _exit_menu_too_long(self):
        maxh = self.h-5
        menu_len = self.menu_options.length
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

    def _set_geometry(self):
        self.h, self.w = self.stdscr.getmaxyx()
        if self.h < 25 or self.w < 80:
            curses.endwin()
            self.log.error("Terminal too small for curses display. "+\
                           "Either use -t/--text for textmode or resize "+\
                            "terminal to at least 80(w)x25(h). "+\
                            f"Current Size: {self.w}(w)x"+\
                            f"{self.h}(h)")
            sys.exit(1)

    def draw_title(self):
        user_str = f"User: {self.username}"
        user_str_start = self.w-len(user_str)-1
        self._addcolorstrs(DIM,[
                [0, 1, f"Host: {self.hostname}"],
                [0, user_str_start, f"User: {self.username}"]])
        self._addcolorstr(self.TITLE_COLOR, 0, 31, self.menu_title)

    def draw_frame(self, uly=None, ulx=None, lry=None, lrx=None, color=DIM):
        color=color
        uly = uly if uly else 1
        ulx = ulx if ulx else 0
        lry = lry if lry else self.h-2
        lrx = lrx if lrx else self.w-1
        i = uly+1
        while i < lry:
            self._addcolorstrs(color,[ [i,ulx,"│"],[i,lrx,"│"] ])
            i=i+1
        frame_width = lrx - ulx + 1
        self._addcolorstrs(color,[
             [uly,ulx,"┌"], [uly,lrx,"┐"], [lry,ulx, "└"], [lry,lrx, "┘"],
             [uly,ulx+1,"─"*(frame_width-2)], [lry,ulx+1,"─"*(frame_width-2)] ])


    def draw_footer(self):
        if self.mode == 'new':
            self._addcolorstrs(DIM,[
                    [self.h-1,14,'Back:'],
                    [self.h-1,28,'Type New Screen Name'],
                    [self.h-1,52,'Accept:']])
            self._addcolorstrs(self.CONTROL_COLOR,[
                    [self.h-1, 19, "<ESC>"],
                    [self.h-1, 59, "<ENTER>"]])
        else:
            self._addcolorstrs(DIM,[
                    [self.h-1,11,'Navigate:'],
                    [self.h-1,25,'Select:'],
                    [self.h-1,41,'New Screen:'],
                    [self.h-1,55,'Quit:'],
                    [self.h-1,65,'|'],
                    [self.h-1,67,'|']])
            self._addcolorstrs(self.CONTROL_COLOR,[
                  [self.h-1, 20, "↑/↓"],
                  [self.h-1, 32, "<ENTER>"],
                  [self.h-1, 52, "N"],
                  [self.h-1, 60, "<ESC>"],
                  [self.h-1, 66, "Q"],
                  [self.h-1, 68, "E"]])

    def _draw_ruler(self, y=False):
        """ dev utility for measuring screen positions """
        y = y if y else self.h-2 # put in place of footer divider if not y
        sect=     "0123456789"
        sect_tens="         1"
        ruler = f'{sect}'*9 # bigger than 80 which is what i design for
        ruler_tens = list(f'{sect_tens}'*9)
        x = 0
        self.stdscr.addstr(y, 0, ruler[:self.w])
        for i,c in enumerate(ruler_tens):
            if c.isdigit():
                 tens = str(int(c)+x)
                 x = x + 1
                 if i < self.w-1:
                     self._addcolorstr(self.CONTROL_COLOR,
                                       y, i+1, f"{tens}")

    def draw_menu(self):
        """
          Draw the menu with the current selection highlighted
        """
        # Draw menu items
        x = self.w//2 - self.menu_max_w//2
        for idx, item in enumerate(self.menu_options, start=1):
            y = self.h//2 - self.menu_len//2 + idx-1
            item_text = f"{item.text: <{self.menu_max_w}}"
            if idx == self.current_row and self.mode == 'menu':
                # Highlight selected item
                self._addcolorstr(self.CONTROL_COLOR|curses.A_BOLD, y, x-2,
                                  f"{self.r_arrow} {item_text} ")
            else:
                self._addcolorstr(self.MENU_COLOR, y, x, item_text)

    def draw_new_entry(self):
        scr_name = "<EMPTY>" if self.new_screen == "" else self.new_screen
        prompt="New Screen Name: "
        name= f"{scr_name: <25}"

        self._addcolorstr(self.CONTROL_COLOR|curses.A_BOLD,
                          self.h-3, 15, self.r_arrow)
        self._addcolorstr(self.CONTROL_COLOR, self.h-3, 17, prompt)
        self._addcolorstr(curses.A_BOLD, self.h-3, 34, name)
        if len(self.new_screen) >= 25:
            self._addcolorstr(DIM,self.h-3, 60,
                              "<max name length>")
    def draw_settings(self):
        self.draw_frame(5,5,20,75,DIM)

    def draw_screen(self):
        """ Draw the full screen """
        self._set_geometry()  # set each loop in case of resize
        self._exit_menu_too_long() # bail if the menu is too long
        self.stdscr.erase()
        self.draw_title()
        self.draw_frame()
        self.draw_menu()
        if self.mode == 'new':
            self.draw_new_entry()
        self.draw_footer()
        #self._draw_ruler(1)
        #self.draw_settings()
        self.stdscr.refresh()

    def input_loop(self, stdscr):
        """Main menu loop"""
        self.stdscr = stdscr
        # Initialize colors
        curses.curs_set(0)  # Hide cursor
        # Only initialize color pair if colors are supported
        if curses.has_colors():
            self._init_colors()

        menu_length = self.menu_options.length
        while True: # main menu draw loop
            self.draw_screen()
            # Get user input
            key = stdscr.getch()
            if key == ord('\n'):  # Enter key
                if self.mode == 'new':
                    if self.new_screen =="":
                        self.mode = 'menu'
                        continue
                    return Option("new",Screen(self.new_screen),"N")
                stdscr.clear()
                curses.endwin()
                return list(self.menu_options)[self.current_row-1]
            elif self.mode == 'new':
               c = chr(key)
               if key in [curses.KEY_BACKSPACE,8,127,curses.KEY_DC]:
                   self.new_screen = self.new_screen[:-1]
                   continue
               elif key == 27: # escape==27
                   self.new_screen = ""
                   self.mode = 'menu'
                   continue
               elif c.isalnum() or c in ['_','-']:
                   if len(self.new_screen) < 25:
                        self.new_screen = f"{self.new_screen}{chr(key)}"
               continue
            elif key == curses.KEY_UP and self.current_row > 1:
                if self.mode == 'menu':
                    self.current_row -= 1
            elif key == curses.KEY_DOWN and self.current_row < menu_length:
                if self.mode == 'menu':
                    self.current_row += 1
            elif key in [27,ord('q'),ord('Q'),ord('e'),ord('E')]: #escape==27
                curses.endwin()
                return False
            elif key in [ord('n'), ord('N')]:
                self.mode = 'new'

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









