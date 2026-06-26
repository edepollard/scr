import subprocess
import sys
from .config import Config, DEFAULT_CONFIG

class ScreenIterator:
    def __init__(self, sessions):
        self.sessions = sessions
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.sessions):
            raise StopIteration
        session = self.sessions[self.index]
        self.index += 1
        return session

class Screen():
    def __init__(self, name=None, pid=None, state=None):
        self.name = name
        self._pid = int(pid) if pid else None
        self.state = state

    def __str__(self):
        return f"name:'{self.name}', pid:{self.pid}, state:'{self.state}'"
    def __repr__(self):
        return\
         f"<Screen name:'{self.name}', pid:{self.pid}, state:'{self.state}'>"

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, n):
        self._name = n

    @property
    def pid(self):
        return self._pid
    @pid.setter
    def pid(self, p):
        if type(p) == int:
            self._pid = p
        else:
            raise TypeError("<Screen>.pid must be of type int.")
    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, s):
        self._state = s

    @property
    def longName(self):
        return f"{self.pid}.{self.name}" if self.is_active else self.name

    @property
    def is_active(self):
        return True if self.pid else False

    def run(self):
        """Attach to existing screen session or create new one,
           then exit process."""
        sesstr = f"{self.pid}.{self.name}" if self.pid else self.name
        scr_opt = '-dr' if self.is_active else '-S'
        scr_cmd = ['screen',scr_opt,self.longName]
        subprocess.run(scr_cmd)
        sys.exit()


class Screens():
    def __init__(self, sessions=[], config=None):
        self._sessions = []
        self.config = config if config else Config(args=args)
        self.color = self.config.color # move calls to this to config.color
        self._log = self.config.log
        self._default = sessions
        self.mergeActive()

    def __iter__(self):
        return ScreenIterator(self.sessions)

    def __str__(self):
        return f"{[str(s) for s in self]}"
    def __repr__(self):
        return f"<Screens {[str(s) for s in self]}"

    @classmethod
    def with_defaults(cls, config=None):
        """Create Screens instance from string or list of strings
           representing session names."""
        config = config if config else Config()
        items = config.default_sessions
        if isinstance(items, str):
            return cls([Screen(name=items)], config=config)
        elif isinstance(items, list):
            if all(isinstance(i, str) for i in items):
                return cls([Screen(name=i) for i in items],
                           config=config)
        raise TypeError("Items added by <Screen>.from_string must be strings.")

    def runningScreens(self):
        """Get all currently running GNU Screen sessions by parsing 
           'screen -ls' output."""
        sessions = []
        ignore_strs=["There are",
                     "There is",
                     "Sockets in",
                     "Socket in",
                     ]
        screens = subprocess.Popen(['screen', '-ls'], stdout=subprocess.PIPE)
        for scr in screens.stdout:
            scr = scr.decode('utf-8')
            if scr.startswith("No Sockets found in"):
                break
            if any(sub in scr for sub in ignore_strs):
                continue
            if scr.strip() == "":
                continue
            ses_name=scr.strip().split('.')[1].split('\t')[0]
            ses_state=scr.strip().split('.')[1].split('\t')[1]
            ses_pid=scr.strip().split('.')[0]
            sessions.append(Screen(name=ses_name,
                                   pid=ses_pid,
                                   state=ses_state))
        return sessions


    def mergeActive(self):
        """Merge running screen sessions with configured defaults,
           updating PIDs and states."""
        for ses in self.runningScreens():
            self.append(ses)
        s_names = [s.name for s in self.sessions]
        [self.append(s) for s in self._default if s.name not in s_names]

    @property
    def log(self):
        return self._log

    @property
    def sessions(self):
        return self._sessions
    @sessions.setter
    def sessions(self, items):
        _new_sessions = []
        if isinstance(items,Screen):
            _new_sessions = [items]
        elif isinstance(items, list):
            for i in items:
                if isinstance(i, Screen):
                    _new_sessions.append(i)
                else:
                    raise TypeError(
                         f"'{self.__class__.__name__}.sessions' "+\
                         "must be <Screen>")
        else:
           raise TypeError(
             f"{self.__class__.__name__}.sessions must be "+\
             "<Screen> or list of <Screen>.")
        self._sessions =  _new_sessions

    def append(self, item):
        """Add a Screen object to the sessions list."""
        if isinstance(item, Screen):
            self._sessions.append(item)
        else:
            raise TypeError(f"{self.__class__.__name__}.screens "+\
                            "items must <Screen> objects.>")

    def insert(self, item):
        """Insert a Screen object to the beginning of thesessions list."""
        if isinstance(item, Screen):
            self._sessions.insert(0,item)
        else:
            raise TypeError(f"{self.__class__.__name__}.screens "+\
                            "items must <Screen> objects.>")

