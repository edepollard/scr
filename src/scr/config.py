from configparser import ConfigParser
import os

DEFAULT_SESSIONS='dev,dev2,run,log,test'
CONFIGFILE=os.path.expanduser("~/.scr")
DEFAULT_CONFIG = { # this is used as a common 
                   #interface is the configfile is missing
                   'scr':{
                           'color': True,
                           'default_sessions': DEFAULT_SESSIONS,
                         }
                 }


class Config():
    def __init__(self, args=None):
        self._cf = self.get_configfile(fname=CONFIGFILE)
        self._color = self.get_item('src','color',default=True)
        self._default_sessions = self.get_item(
                           'src',
                           'default_sessions',
                           default=DEFAULT_SESSIONS).split(',')


        if args:
            if args['nocolor']:
                self._color = False
            if args['default_sessions']:
                self._default_sessions = args['default_sessions'].split(',')

    @property
    def default_sessions(self):
        return self._default_sessions

    @property
    def color(self):
        return self._color

    @property
    def cf(self):
        return self._cf

    def get_configfile(self,fname=CONFIGFILE):
        cf = ConfigParser()
        if os.path.isfile(fname):
            cf.read(fname)
        else:
            cf['scr'] = DEFAULT_CONFIG['scr']
        return cf

    def get_item(self,section,item,default=None):
        if self.cf.has_option(section, item):
            return self.cf[section][option]
        return default

