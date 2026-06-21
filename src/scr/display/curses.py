from .options import Options, Option
from scr.screen import Screen
from scr.config import Config
import curses
import os
import sys
from socket import gethostname
from getpass import getuser
import traceback


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

class CursesElement():

    def __getattr__(self, name):
        if name in self.COLORS:
            return self.COLORS[name]
        raise AttributeError(f"'{type(self).__name__}' "+\
                             f"object has no attribute '{name}'")
    @property
    def COLORS(self):
        if '_COLORS' not in self.__dict__:
            self._COLORS = {
                'BLACK' : curses.COLOR_BLACK,
                'WHITE' : curses.COLOR_WHITE,
                'CYAN' : curses.COLOR_CYAN,
                'GREEN' : curses.COLOR_GREEN,
                'MAGENTA' : curses.COLOR_MAGENTA,
                'YELLOW' : curses.COLOR_YELLOW,
                'RED' : curses.COLOR_RED,
                'BLUE' : curses.COLOR_BLUE,
                'DIM' : curses.A_DIM,
                'REV' : curses.A_REVERSE,
            }
        return self._COLORS

    @property
    def config(self):
        if '_config' not in self.__dict__:
            self._config = Config()
        return self._config
    @config.setter
    def config(self, cfg):
        if not isinstance(cfg, Config):
            raise TypeError(
               f"'{type(self).__name__}.config' must be an instance of Config")
        self._config = cfg

    @property
    def colors(self):
        if '_colors' not in self.__dict__:
            self._colors={
                'highlight' : self.color_pair(1, self.BLACK, self.WHITE),
                'cyan'      : self.color_pair(2, self.CYAN, self.BLACK),
                'green'     : self.color_pair(3, self.GREEN, self.BLACK),
                'magenta'   : self.color_pair(4, self.MAGENTA, self.BLACK),
                'yellow'    : self.color_pair(5, self.YELLOW, self.BLACK),
                'red'       : self.color_pair(6, self.RED, self.BLACK),
                'blue'      : self.color_pair(7, self.BLUE, self.BLACK),
               }
        return self._colors

    def color_pair(self, index, foreground, background):
        curses.init_pair(index,foreground,background)
        return curses.color_pair(index)

    @property
    def MENU_COLOR(self):
        return self.colors[self.config.menu_color]

    @property
    def TITLE_COLOR(self):
        return self.colors[self.config.title_color]

    @property
    def CONTROL_COLOR(self):
        return self.colors[self.config.control_color]

    @property
    def h(self):
        if '_h' not in self.__dict__:
            self.set_geometry()
        return self._h
    @h.setter
    def h(self, i):
        if not isinstance(i, int):
            raise TypeError(f"'{type(self).__name__}.h' must be of type 'int'>")
        self._h = i

    @property
    def w(self):
        if '_w' not in self.__dict__:
            self.set_geometry()
        return self._w
    @w.setter
    def w(self, i):
        if not isinstance(i, int):
            raise TypeError(f"'{type(self).__name__}.w' must be of type 'int'>")
        self._w = i

    @property
    def stdscr(self):
        if '_stdstr' not in self.__dict__:
            self._stdstr = False
        return self._stdscr
    @stdscr.setter
    def stdscr(self, s):
        self._stdscr = s

    def set_geometry(self):
        self._h, self._w = self.stdscr.getmaxyx()
        if self._h < 25 or self._w < 80:
            self._exit_screen_bad_size()

    def _exit_screen_bad_size(self):
        curses.endwin()
        self.log.error("Terminal too small for curses display. "+\
                       "Either use -t/--text for textmode or resize "+\
                       "terminal to at least 80(w)x25(h). "+\
                       f"Current Size: {self.w}(w)x"+\
                       f"{self.h}(h)")
        sys.exit(1)


    def addcolorstr(self, color, *args, **kwargs):
        if self.config.color:
            self.stdscr.attron(color)
        self.stdscr.addstr(*args, **kwargs)
        if self.config.color:
            self.stdscr.attroff(color)

    def addcolorstrs(self, color, strs=[]):
        if self.config.color:
            self.stdscr.attron(color)
        for s in strs:
            self.stdscr.addstr(s[0], s[1], s[2])
        if self.config.color:
            self.stdscr.attroff(color)

    def draw_frame(self, uly=None, ulx=None,
                         lry=None, lrx=None, color=None):
        color = color if color else self.DIM
        uly = uly if uly else 1
        ulx = ulx if ulx else 0
        lry = lry if lry else self.h-2
        lrx = lrx if lrx else self.w-1
        i = uly+1
        while i < lry:
            self.addcolorstrs(color,[ [i,ulx,"│"],[i,lrx,"│"] ])
            i=i+1
        frame_width = lrx - ulx + 1
        self.addcolorstrs(color,[
             [uly,ulx,"┌"], [uly,lrx,"┐"], [lry,ulx, "└"], [lry,lrx, "┘"],
             [uly,ulx+1,"─"*(frame_width-2)], [lry,ulx+1,"─"*(frame_width-2)] ])

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
                     self.addcolorstr(self.CONTROL_COLOR,
                                       y, i+1, f"{tens}")

class Menu(CursesElement):
    def __init__(self, stdscr=None, config=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self._stdscr = stdscr
        self.current_row = 1
        self._menu_max_w = None
        self._menu_len = False
        self.active=True
        self.r_arrow = "➤"
        self._menu = {
                       'title':None,
                       'options':Options(),
                       'controls':Options(allow_duplicates=False)
                     }

    @property
    def stdscr(self):
        return self._stdscr
    @stdscr.setter
    def stdscr(self, s):
        self._stdscr = s

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
    def options(self):
        return self._menu['options']
    @options.setter
    def options(self,opts):
        self._menu['options']=Options(opts)
    @property
    def menu_controls(self):
        return self._menu['controls']
    @menu_controls.setter
    def menu_controls(self,opts):
        self._menu['controls']=Options(opts, allow_duplicates=False)

    @property
    def menu_max_w(self):
        if not self._menu_max_w or not self.menu_len:
            self._menu_max_w = max([len(i.text) for i in self.options])
        return self._menu_max_w

    @property
    def menu_len(self):
        if not self._menu_len:
            self._menu_len = self.options.length
        return self._menu_len

    @property
    def option(self):
        return Option
    @property
    def control(self):
        return Option.control

    def menu_input(self):
       key = self.stdscr.getch()
       if key == ord('\n'):  # Enter key
           self.stdscr.clear()
           curses.endwin()
           return list(self.options)[self.current_row-1]
       elif key == curses.KEY_UP and self.current_row > 1:
           self.current_row -= 1
       elif key == curses.KEY_DOWN and self.current_row < self.menu_len:
           self.current_row += 1
       elif key in [27,ord('q'),ord('Q'),ord('e'),ord('E')]: #escape==27
           curses.endwin()
           exit()
       elif key in [ord('n'), ord('N')]:
           self.active = False
           return "new"


    def _exit_menu_too_long(self):
        maxh = self.h-5
        menu_len = self.options.length
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

    def draw_menu(self):
        """
          Draw the menu with the current selection highlighted
        """
        self._exit_menu_too_long()
        x = self.w//2 - self.menu_max_w//2
        for idx, item in enumerate(self.options, start=1):
            y = self.h//2 - self.menu_len//2 + idx-1
            item_text = f"{item.text: <{self.menu_max_w}}"
            if idx == self.current_row and self.active:
                # Highlight selected item
                self.addcolorstr(self.CONTROL_COLOR|curses.A_BOLD, y, x-2,
                                  f"{self.r_arrow} {item_text} ")
            else:
                self.addcolorstr(self.MENU_COLOR, y, x, item_text)


class CursesDisplay(CursesElement):
    def __init__(self, config=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self.style = "curses"
        self.new_screen = ""
        self.current_row = 1
        self._menu_max_w = None
        self._menu_len = False
        self.r_arrow = "➤"
        self._main_menu = False
        self._display = {
                        'title':None,
                        }

    @property
    def display_title(self):
        return self._display['title']
    @display_title.setter
    def display_title(self,t):
        if isinstance(t, str):
            self._display['title'] = t
            return
        raise TypeError("CursesDisplay title must be of type 'str'")

    @property
    def main_menu(self):
        if not self._main_menu:
            self._main_menu = Menu(config=self.config)
        return self._main_menu

    @property
    def menu_options(self):
        return self.main_menu.options
    @menu_options.setter
    def menu_options(self,opts):
        self.main_menu.options=opts

    @property
    def menu_controls(self):
        return self.main_menu.menu_controls
    @menu_controls.setter
    def menu_controls(self,opts):
        self.main_menu.controls=opts

    @property
    def option(self):
        return Option
    @property
    def control(self):
        return Option.control

    @property
    def hostname(self):
        return gethostname().split('.')[0]

    @property
    def username(self):
        return getuser()

    @property
    def modes(self):
        if '_modes'  not in self.__dict__:
            self._modes = {'new','menu'}
        return self._modes
    @modes.setter
    def modes(self, new_modes):
        if type(new_modes) not in [list,tuple,dict]:
            raise ValueError(
             f"'{type(self).__name__}.modes must be one of [list,tuple,dict]'")
        self._modes = {i for i in new_modes}

    @property
    def mode(self):
        if '_mode' not in self.__dict__:
            self._mode = 'menu'
        return self._mode
    @mode.setter
    def mode(self, m):
        if m not in self.modes:
            raise ValueError(
                   f"'{type(self).__name__}.mode must be one of {self.modes}'")
        if m == 'menu':
            self._mode = 'menu'
            self.main_menu.active = True
        if m == 'new':
            self._mode = 'new'
            self.main_menu.active = False

    def __str__(self):
        return self.style
    def __repr__(self):
        return "<class 'CursesDisplay'>"

    def draw_title(self):
        user_str = f"User: {self.username}"
        user_str_start = self.w-len(user_str)-1
        self.addcolorstrs(self.DIM,[
                [0, 1, f"Host: {self.hostname}"],
                [0, user_str_start, f"User: {self.username}"]])
        self.addcolorstr(self.TITLE_COLOR, 0, 31, self.display_title)

    def draw_footer(self):
        if self.mode == 'new':
            self.addcolorstrs(self.DIM,[
                    [self.h-1,14,'Back:'],
                    [self.h-1,28,'Type New Screen Name'],
                    [self.h-1,52,'Accept:']])
            self.addcolorstrs(self.CONTROL_COLOR,[
                    [self.h-1, 19, "<ESC>"],
                    [self.h-1, 59, "<ENTER>"]])
        else:
            self.addcolorstrs(self.DIM,[
                    [self.h-1,11,'Navigate:'],
                    [self.h-1,25,'Select:'],
                    [self.h-1,41,'New Screen:'],
                    [self.h-1,55,'Quit:'],
                    [self.h-1,65,'|'],
                    [self.h-1,67,'|']])
            self.addcolorstrs(self.CONTROL_COLOR,[
                  [self.h-1, 20, "↑/↓"],
                  [self.h-1, 32, "<ENTER>"],
                  [self.h-1, 52, "N"],
                  [self.h-1, 60, "<ESC>"],
                  [self.h-1, 66, "Q"],
                  [self.h-1, 68, "E"]])

    def draw_new_entry(self):
        scr_name = "<EMPTY>" if self.new_screen == "" else self.new_screen
        prompt="New Screen Name: "
        name= f"{scr_name: <25}"

        self.addcolorstr(self.CONTROL_COLOR|curses.A_BOLD,
                          self.h-3, 15, self.r_arrow)
        self.addcolorstr(self.CONTROL_COLOR, self.h-3, 17, prompt)
        self.addcolorstr(curses.A_BOLD, self.h-3, 34, name)
        if len(self.new_screen) >= 25:
            self.addcolorstr(self.DIM,self.h-3, 60,
                              "<max name length>")
    def draw_settings(self):
        self.draw_frame(5,5,20,75,self.DIM)

    def draw_screen(self):
        """ Draw the full screen """
        self.set_geometry()  # set each loop in case of resize
        self.stdscr.erase()
        self.draw_title()
        self.draw_frame()
        self.main_menu.draw_menu()
        if self.mode == 'new':
            self.draw_new_entry()
        self.draw_footer()
        #self._draw_ruler(1)
        #self.draw_settings()
        self.stdscr.refresh()

    def new_screen_input(self):
        key = self.stdscr.getch()
        if key == ord("\n"):
            if self.new_screen =="":
                return 'menu'
            return Option("new",Screen(self.new_screen),"N")
        elif key in [curses.KEY_BACKSPACE,8,127,curses.KEY_DC]:
            self.new_screen = self.new_screen[:-1]
        elif key == 27: # escape==27
            self.new_screen = ""
            return 'menu'
        elif chr(key).isalnum() or chr(key) in ['_','-']:
            # [1-9,a-z,A-Z,_,-]
            if len(self.new_screen) < 25:
                 self.new_screen = f"{self.new_screen}{chr(key)}"

    def main_loop(self):
        """Main menu loop"""
        while True:
            self.draw_screen()
            if self.mode == 'menu':
                ret = self.main_menu.menu_input()
            elif self.mode == 'new':
                ret = self.new_screen_input()
            if isinstance(ret, Option):
                curses.endwin()
                ret.action.run()
                sys.exit()
            if ret in self.modes:
                self.mode = ret

    def run(self, stdscr):
        self.stdscr = stdscr
        self.main_menu.stdscr=stdscr
        curses.curs_set(0)  # Hide cursor
        if not curses.has_colors():
            self.config.color=False
        self.main_loop()

    def menu(self):
        # Set TERM environment variable if not set
        os.environ.setdefault('ESCDELAY','25')
        if 'TERM' not in os.environ:
            os.environ['TERM'] = 'xterm-256color'
        try:
            ret = curses.wrapper(self.run)
        except curses.error as e:
            traceback.print_exc()
            print(f"\nError: {e}")
            print("This script requires a proper terminal environment.")









