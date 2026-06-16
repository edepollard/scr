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
                         }
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
        self._args = args
        self._log = Log(color=self.color)

        # allow args from click/commandline to override config file
        if args:
            if args['text'] and args['curses']:
                self.log.error(
                      " -t/--text and -c/--curses are mutally exclusive, "+\
                      " please choose only one.", fatal=True)
            if args['nocolor']:
                self._color = False
            if args['default_sessions']:
                self._default_sessions = args['default_sessions'].split(',')
            if args['curses']:
                self._style = 'curses'
            if args['text']:
                self._style = 'text'


    @property
    def default_sessions(self):
        return self._default_sessions

    @property
    def color(self):
        return self._color

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

