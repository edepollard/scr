from configparser import ConfigParser
import os
from scr.log import Log

DEFAULT_SESSIONS='dev,dev2,run,log,test'
DEFAULT_COLOR=True
DEFAULT_STYLE='text'

CONFIGFILE=os.path.expanduser("~/.scr")

DEFAULT_CONFIG = {
                   # this is used as a common interface if
                   # the configfile is missing
                   'scr':{
                           'color': DEFAULT_COLOR,
                           'default_sessions': DEFAULT_SESSIONS,
                           'style': DEFAULT_STYLE,
                           'title_color': 'cyan',
                           'menu_color': 'green',
                           'control_color': 'magenta',
                           'select':'both',
                         }
                 }

AVAILABLE_COLORS = {'cyan'    :'[[C]]',
                    'green'   :'[[G]]',
                    'magenta' :'[[P]]',
                    'yellow'  :'[[Y]]',
                    'red'     :'[[R]]',
                    'blue'    :'[[B]]',
                   }


class Config():
    def __init__(self, args=None):
        self._cf = self.get_configfile(fname=CONFIGFILE)
        self._color = self.get_bool('scr','color',
                           default=DEFAULT_CONFIG['scr']['color'])
        self._default_sessions = self.get_item(
                           'scr',
                           'default_sessions',
                           default=DEFAULT_SESSIONS).split(',')
        self._style = self.get_item('scr','style',
                           default=DEFAULT_CONFIG['scr']['style'])
        self._title_color = False
        self._menu_color = False
        self._control_color = False
        self.title_color = self.get_item('scr', 'title_color',
                           default=DEFAULT_CONFIG['scr']['title_color'])
        self.menu_color = self.get_item('scr', 'menu_color',
                           default=DEFAULT_CONFIG['scr']['menu_color'])
        self.control_color = self.get_item('scr', 'control_color',
                           default=DEFAULT_CONFIG['scr']['control_color'])
        self._select = self.get_item('scr','select',
                           default=DEFAULT_CONFIG['scr']['select'])
        self._args = args

        # allow args from click/commandline to override config file
        if args:
            if args['text'] and args['curses']:
                print(" -t/--text and -c/--curses are mutally exclusive, "+\
                      " please choose only one.")
                exit(1)
            if args['nocolor']:
                self._color = False
            if args['default_sessions']:
                self._default_sessions = args['default_sessions'].split(',')
            if args['curses']:
                self._style = 'curses'
            if args['text']:
                self._style = 'text'

        self._log = Log(color=self.color)
        if args and args['all_colors']:
            self.print_available_colors()
            exit()


    @property
    def default_sessions(self):
        return self._default_sessions
    @default_sessions.setter
    def default_sessions(self, items):
        self._default_sessions = [i.strip() for i in items.split(',')]

    @property
    def color(self):
        return self._color
    @color.setter
    def color(self,c):
        if not isinstance(c, bool):
            raise TypeError('Config.color must be set to a boolean.')
        self._color = True if c else False

    @property
    def title_color(self):
        return self._title_color
    @title_color.setter
    def title_color(self,c):
        if c.lower().strip() in AVAILABLE_COLORS:
            self._title_color = c.lower().strip()
            return
        raise Exception(f"'{c}' not in available colors: {AVAILABLE_COLORS}")
    @property
    def menu_color(self):
        return self._menu_color
    @menu_color.setter
    def menu_color(self,c):
        if c.lower().strip() in AVAILABLE_COLORS:
            self._menu_color = c.lower().strip()
            return
        raise Exception(f"'{c}' not in available colors: {AVAILABLE_COLORS}")
    @property
    def control_color(self):
        return self._control_color
    @control_color.setter
    def control_color(self,c):
        if c.lower().strip() in AVAILABLE_COLORS:
            self._control_color = c.lower().strip()
            return
        raise Exception(f"'{c}' not in available colors: {AVAILABLE_COLORS}")

    @property
    def select(self):
        return self._select
    @select.setter
    def select(self, s):
        if s not in ['arrow','highlight','both']:
            raise ValueError("Config.select must be one of "+\
                             "['arrow','highlight','both']")
        self._select = s

    @property
    def cf(self):
        return self._cf

    @property
    def log(self):
        return self._log

    @property
    def style(self):
        return self._style
    @style.setter
    def style(self, s):
        if not isinstance(s, str):
            raise TypeError(f"Style must be a string not {type(s)}")
        if s.lower() in ['text','curses']:
            self._style = s.lower()
        else:
            raise Exception("Style must be wither 'text' or 'curses'")

    @property
    def args(self):
        return self._args

    def save(self):
        c = ConfigParser()
        c['scr']={
           'color':self.color,
           'default_sessions': ",".join(self.default_sessions),
           'style':self.style,
           'menu_color':self.menu_color,
           'title_color':self.title_color,
           'control_color':self.control_color,
           'select':self.select,
        }
        with open(CONFIGFILE, 'w', encoding='utf-8') as cf:
            c.write(cf)

    def print_available_colors(self):
        ac = [f"{AVAILABLE_COLORS[c]}{c}[[E]]" for c in AVAILABLE_COLORS ]
        self.log(f"Available Colors: {','.join([c for c in ac])}")

    def get_text_color(self, cname):
        if cname in AVAILABLE_COLORS:
            return AVAILABLE_COLORS[cname]
        return None

    def get_configfile(self,fname=CONFIGFILE):
        """
          Load config file if it exists, otherwise return 
          default configuration.
        """
        cf = ConfigParser()
        if os.path.isfile(fname):
            cf.read(fname)
        else:
            cf.read_dict(DEFAULT_CONFIG)
        return cf

    def get_item(self,section,item,default=None):
        """
          Retrieve a config value from the specified section,
          returning default if not found.
        """
        if self.cf.has_option(section, item):
            return self.cf[section][item]
        return default
    def get_bool(self,section,item,default=None):
        if self.cf.has_option(section,item):
            return self.cf.getboolean(section,item)
        return default

