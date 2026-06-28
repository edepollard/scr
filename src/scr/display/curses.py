from .options import Options, Option
from scr.screen import Screen
from scr.config import Config
import curses
from curses import textpad
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
                'white'     : self.color_pair(8, self.WHITE, self.BLACK),
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
    def r_arrow(self):
        return "➤"

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
                         lry=None, lrx=None,
                         color=None, fill=False):
        color = color if color else self.DIM
        uly = uly if uly else 1
        ulx = ulx if ulx else 0
        lry = lry if lry else self.h-2
        lrx = lrx if lrx else self.w-1
        i = uly+1
        if fill:
            filler = " "*((lrx-ulx)-1)
        while i < lry:
            self.addcolorstrs(color,[ [i,ulx,"│"],[i,lrx,"│"] ])
            if fill:
                self.addcolorstr(color,i,ulx+1,filler)
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
    def __init__(self, stdscr=None, config=None, select=False):
        self.config = config if config else Config()
        self.log = self.config.log
        self._stdscr = stdscr
        self._current_row = 0
        self._start_row = 0
        self._selected_item = None
        self._menu_max_w = None
        self._menu_len = False
        self.active=True
        if select:
             self.select = select
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

        return min(self._menu_max_w, self.w-10)

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

    @property
    def select(self):
        return self.config.select
    @select.setter
    def select(self, s):
        self.config.select = s

    def menu_input(self):
        key = self.stdscr.getch()
        if key == ord('\n'):  # Enter key
            self.stdscr.clear()
            curses.endwin()
            return self.selected_item
        elif key == curses.KEY_UP and self.current_row > 0:
            self.current_row -= 1
        elif key == curses.KEY_DOWN and self.current_row < self.menu_len:
            self.current_row += 1
        elif key in [27,ord('q'),ord('Q'),ord('e'),ord('E')]: #escape==27
            curses.endwin()
            exit()
        elif key in [ord('n'), ord('N')]:
            self.active = False
            return "new"
        elif key in [ord('s'), ord('S')]:
            self.active = False
            return "settings"

    @property
    def start_row(self):
        return self._start_row
    @start_row.setter
    def start_row(self,i):
        self._start_row = i
    @property
    def current_row(self):
        return self._current_row
    @current_row.setter
    def current_row(self, i):
        if i < 0:
            self._current_row = 0
        if i >= self.menu_len:
            self._current_row = self.menu_len-1
        else:
            self._current_row = i
        if self._current_row < self.start_row:
            self.start_row = self._current_row
        if self._current_row >= self.start_row + self.h - 7:
            self.start_row = self.current_row  - self.h + 8

    @property
    def selected_item(self):
        return self._selected_item
    @selected_item.setter
    def selected_item(self, i):
        self._selected_item = i

    def draw_menu(self):
        """
          Draw the menu with the current selection highlighted
        """
        _y = self.h//2 - min(self.h-7,self.menu_len)//2
        x = self.w//2 - self.menu_max_w//2
        #self.draw_frame(_y-1,x-1,
        #                _y+(min(self.h-7,self.menu_len)),x+self.menu_max_w)
        opts = [i for i in self.options]
        selected_item=None
        for i in range(min(self.menu_len,self.h - 7)):
            idx = self.start_row + i
            if idx >= self.menu_len:
                break
            y = _y + i
            item = opts[idx]
            item_text = f"{item.text: <{self.menu_max_w}}"
            item_text = item_text[:self.w-10]
            if not self.config.color:
                select = 'arrow'
            else:
                select = self.select
            if idx == self.current_row and self.active:
                self.selected_item = item
                # Highlight selected item
                if select == "arrow":
                    color = self.CONTROL_COLOR|curses.A_BOLD
                    arrow = f"{self.r_arrow}"
                    text = f"{item_text}"
                    _x = x-2
                elif select == "highlight":
                    color = self.CONTROL_COLOR|self.REV
                    arrow = ""
                    text = f"{item_text}"
                    _x = x
                else:
                    color = self.CONTROL_COLOR|self.REV
                    arrow = f"{self.r_arrow}"
                    text = f"{item_text}"
                    _x = x-2
                self.addcolorstr(self.CONTROL_COLOR|curses.A_BOLD,
                                 y, _x, arrow)
                self.addcolorstr(color, y, x,text)
            else:
                self.addcolorstr(self.MENU_COLOR, y, x, item_text)
        if self.start_row+self.h-7 < self.menu_len:
            self.addcolorstr(self.DIM,
                             _y+(min(self.h-7,self.menu_len)-1),x-3, "▼")
        if self.start_row > 0:
            self.addcolorstr(self.DIM, _y, x-3, "▲")

class CursesDisplay(CursesElement):
    def __init__(self, config=None):
        self.config = config if config else Config()
        self.log = self.config.log
        self.style = "curses"
        self.new_screen = ""
        self.current_row = 1
        self.settings_color = False
        self.settings_show_picker = False
        self.disp_saved = False
        self._menu_max_w = None
        self._menu_len = False
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
            self._modes = {'new','menu','settings','default_sessions'}
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
        if m == 'settings':
            self._mode = 'settings'
            self.main_menu.active = False
        if m == 'default_sessions':
            self._mode = 'default_sessions'
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
        elif self.mode == 'menu':
            self.addcolorstrs(self.DIM,[
                    [self.h-1,5,'NAVIGATE:'],
                    [self.h-1,19,'SELECT:'],
                    [self.h-1,35,'NEW SCREEN:'],
                    [self.h-1,49,'SETTINGS:'],
                    [self.h-1,61,'QUIT:'],
                    [self.h-1,71,'|'],
                    [self.h-1,73,'|']])
            self.addcolorstrs(self.CONTROL_COLOR,[
                    [self.h-1, 14, "↑/↓"],
                    [self.h-1, 26, "<ENTER>"],
                    [self.h-1, 46, "N"],
                    [self.h-1, 58, "S"],
                    [self.h-1, 66, "<ESC>"],
                    [self.h-1, 72, "Q"],
                    [self.h-1, 74, "E"]])
        elif self.mode == 'settings':
            self.addcolorstrs(self.DIM,[
                    [self.h-1,14,'BACK:'],
                    [self.h-1,36,'SAVE:'],
                    [self.h-1,55,'QUIT:'],
                    [self.h-1,61,'|']])

            self.addcolorstrs(self.CONTROL_COLOR,[
                    [self.h-1, 19, "<ESC>"],
                    [self.h-1, 41, "S"],
                    [self.h-1, 60, "Q"],
                    [self.h-1, 62, "E"]])
        elif self.mode == 'default_sessions':
            self.addcolorstrs(self.DIM,[
                    [self.h-1,2,'CANCEL:'],
                    [self.h-1,18,'ACCEPT:'],
                    [self.h-1,36,'TYPE COMMA SEPARATED LIST'],
                    [self.h-1,65,'QUIT:']])

            self.addcolorstrs(self.CONTROL_COLOR,[
                    [self.h-1, 9, "<ESC>"],
                    [self.h-1, 25, "<ENTER>"],
                    [self.h-1, 70, "<CTRL-E>"]])

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

    def highlight_selection(self, y, x, text, style=False, sel=False):
        ''' Leave 2 charracters to left of x for arrow'''
        arrow = False
        style = style if style else self.config.select
        select = self.config.select

        if style == "arrow":
            selected = True if style == select else False
            color = self.CONTROL_COLOR|curses.A_BOLD
            arrow = True
        elif style == "highlight":
            selected = True if style == select else False
            color = self.CONTROL_COLOR|self.REV
        elif style == "both":
            selected = True if style == select else False
            color = self.CONTROL_COLOR|self.REV
            arrow = True
        if arrow:
            self.addcolorstr(self.CONTROL_COLOR|curses.A_BOLD,
                             y, x-2,self.r_arrow)
        self.addcolorstr(color, y, x, text)
        if selected and not sel:
            self.addcolorstr(curses.A_BOLD, y, x+len(text)+1 ,"←")
            self.addcolorstr(curses.A_DIM, y, x+len(text)+3 ,"Selected")

    def draw_default_sessions(self):
        uly, ulx = 5, 15
        # title
        y, x = uly+1, ulx+17
        title="Default Sessions"
        self.addcolorstr(self.TITLE_COLOR, y, x, title)

        y, x = uly+2, ulx+4
        self.draw_frame(y,x,y+9,x+42,self.DIM, fill=True)
        self.draw_footer()
        self.tp = curses.newwin(8,41,y+1,x+1)
        self.tp.addstr(0,0, ",".join(self.config.default_sessions))
        self.stdscr.refresh()
        self.tp_editor = textpad.Textbox(self.tp)
        curses.curs_set(1)  # show cursor
        self.tp_editor.edit(self.editor_input)
        curses.curs_set(0)  # Hide cursor
        ds = self.tp_editor.gather().strip()
        ds = ",".join([s.strip().replace(' ','_')\
                        for s in ds.split(',') if s.strip()!=''])
        self.config.default_sessions = ds

    def editor_input(self,key):
        if key == 5: # ctrl-e
            curses.endwin()
            sys.exit()
        if key == 27: # escape
            self.tp.erase()
            self.tp.addstr(0,0,",".join(self.config.default_sessions))
            return 7 # ctrl-g
        if key in [8, 127]: # backspace and delete
            return 8
        if key == ord("\n"):
            return 7
        if any([chr(key).isalnum(),key in [ord(','),ord('-'),ord('_')]]):
            return key
        return None

    def draw_settings(self):
        uly, ulx = 5, 15
        self.draw_frame(uly,ulx,uly+15,ulx+50,self.DIM, fill=True)

        # title
        y, x = uly+1, ulx+21
        title="Settings"
        self.addcolorstr(self.TITLE_COLOR, y, x, title)

        # Color on/off
        y, x = uly+2, ulx+2
        c = "On" if self.config.color else "Off"
        self.draw_control(y,x,'O'," ", color=self.config.control_color)
        self.addcolorstr(self.colors['white'], y, x+2, "Color")
        self.addcolorstr(curses.A_BOLD, y, x+12, c)

        # Color selections
        y,x = uly+4, ulx+2
        self.draw_color_setting(y, x, 'T', 'title', 'Title',
                                self.TITLE_COLOR, self.config.title_color)
        self.draw_color_setting(y+1, x, 'M', 'menu', 'Menu',
                                self.MENU_COLOR, self.config.menu_color)
        self.draw_color_setting(y+2, x, 'C', 'control', 'Control',
                                self.CONTROL_COLOR, self.config.control_color)

        # toggle select indicator
        y, x = uly+9, ulx+2
        self.draw_control(y,x,'Z'," ",color=self.config.control_color)
        self.addcolorstr(self.colors['white'],y,x+2,'Select Style')
        self.highlight_selection(y,x+18,"Arrow and Reverse", 'both')
        self.highlight_selection(y+1,x+18,"Arrow", 'arrow')
        self.highlight_selection(y+2,x+18,"Reverse", 'highlight')

        y, x = uly+13, ulx+2
        self.draw_control(y,x,'D'," ",color=self.config.control_color)
        self.addcolorstr(self.colors['white'],y,x+2,'Default Sessions')
        def_str = ','.join(self.config.default_sessions)
        if len(def_str) > 34:
            def_str = def_str[:34]+"..."
        self.addcolorstr(self.DIM,y+1,x+9, f"[{' '*37}]")
        self.addcolorstr(self.colors['white'],y+1,x+10,def_str)

        # save confirmed message
        y, x = uly+15, ulx+18
        if self.disp_saved:
            self.addcolorstr(self.DIM, y, x, "< Config Saved >")
            self.disp_saved = False

        # color options display
        y, x = uly+3, ulx+24
        if self.settings_color:
            self.draw_control(y,   x, 'L', 'Light Blue/Cyan', 'cyan')
            self.draw_control(y+1, x, 'G', 'Green', 'green')
            self.draw_control(y+2, x, 'Y', 'Yellow', 'yellow')
            self.draw_control(y+3, x, 'P', 'Magenta/Purple', 'magenta')
            self.draw_control(y+4, x, 'R', 'Red', 'red')
            self.draw_control(y+5, x, 'B', 'Blue', 'blue')

    def draw_color_setting(self, y, x, key, setting, label, color, cname):
        if self.settings_color == setting:
            self.highlight_selection(y,x+2,label,sel=True)
        else:
            self.addcolorstr(self.colors['white'],y,x+2,label)
            self.draw_control(y,x,key, color=self.config.control_color)
            self.addcolorstr(self.DIM, y, x+1,":")
        self.addcolorstr(color, y, x+12, cname)



    def draw_control(self, y, x, control, label=False, color=False,
                                sep=':', rev=False):
            col = self.colors[color] if color else self.DIM
            if rev:
                if label:
                    self.addcolorstr(self.DIM, y, x, f"{label}{sep}")
                    self.addcolorstr(col,y,x,label)
                    self.addcolorstr(self.CONTROL_COLOR,
                                     y, (x+len(label)+len(sep)), control)
                else:
                    self.addcolorstr(col,y,x,control)

            else:
                if label:
                    self.addcolorstr(self.DIM, y, x, f"{control}{sep}")
                    self.addcolorstr(self.CONTROL_COLOR, y, x, control)
                    self.addcolorstr(col,
                                     y, (x+len(control)+len(sep)), label)
                else:
                    self.addcolorstr(col,y,x,control)


    def draw_screen(self):
        """ Draw the full screen """
        self.set_geometry()  # set each loop in case of resize
        self.stdscr.erase()
        self.draw_title()
        self.draw_frame()
        if self.mode == 'menu':
            self.main_menu.draw_menu()
        if self.mode == 'new':
            self.main_menu.draw_menu()
            self.draw_new_entry()
        if self.mode == 'settings':
            self.draw_settings()
        if self.mode == 'default_sessions':
            self.draw_default_sessions()
        self.draw_footer()
        #self._draw_ruler()
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

    def set_setting_color(self,key, lc, uc, setting, color):
        if key in [ord(lc), ord(uc)]:
            if setting == 'title':
                self.config.title_color = color
            if setting == 'menu':
                self.config.menu_color = color
            if setting == 'control':
                self.config.control_color = color
            self.settings_color = False


    def assign_color(self, setting, key):
        self.set_setting_color(key, 'g','G',setting,'green')
        self.set_setting_color(key, 'y','Y',setting,'yellow')
        self.set_setting_color(key, 'l','L',setting,'cyan')
        self.set_setting_color(key, 'b','B',setting,'blue')
        self.set_setting_color(key, 'r','R',setting,'red')
        self.set_setting_color(key, 'p','P',setting,'magenta')

    def settings_input(self):
        key = self.stdscr.getch()
        if self.settings_color:
            self.assign_color(self.settings_color, key)
            if key == 27:
                self.settings_color = False
                return
        if key in [ord('q'),ord('Q'),ord('e'),ord('E')]: #escape==27
            curses.endwin()
            exit()
        elif key in [ord('o'), ord('O')]:
            if self.config.color:
                self.config.color=False
            else:
                self.config.color=True
        elif key in [ord('t'), ord('T')]:
            self.settings_color = 'title'
        elif key in [ord('m'), ord('M')]:
            self.settings_color = 'menu'
        elif key in [ord('c'), ord('C')]:
            self.settings_color = 'control'
        elif key in [ord('z'), ord('Z')]:
            self.toggle_select()
        elif key in [ord('s'), ord('S')]:
            self.config.save()
            self.disp_saved = True
        elif key in [ord('d'), ord('D')]:
            self.mode = 'default_sessions'
        elif key == 27: # escape==27
            return 'menu'

    def default_sessions_input(self):
        return 'settings'
        key = self.stdscr.getch()
        if key in [ord('q'),ord('Q'),ord('e'),ord('E')]: #escape==27
            curses.endwin()
            exit()
        if key == ord("\n"):
            #if self.new_default_screens =="":
            #    return 'settings'
            return 'settings'
            return Option("new",Screen(self.new_screen),"N")
        elif key == 27: # escape==27
            return 'settings'

    def toggle_select(self):
        if self.config.select == 'both':
            self.config.select = 'arrow'
        elif self.config.select == 'highlight':
            self.config.select = 'both'
        elif self.config.select == 'arrow':
            self.config.select = 'highlight'
        return

    def main_loop(self):
        """Main menu loop"""
        while True:
            self.draw_screen()
            if self.mode == 'menu':
                ret = self.main_menu.menu_input()
            elif self.mode == 'new':
                ret = self.new_screen_input()
            elif self.mode == 'settings':
                ret = self.settings_input()
            elif self.mode == 'default_sessions':
                ret = self.default_sessions_input()
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









