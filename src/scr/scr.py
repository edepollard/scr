import subprocess
import sys
from .config import Config, DEFAULT_CONFIG
from .display.scrdisplay import ScrDisplay

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
        """Attach to existing screen session or create new one, then exit process."""
        sesstr = f"{self.pid}.{self.name}" if self.pid else self.name
        scr_opt = '-dr' if self.is_active else '-S'
        scr_cmd = ['screen',scr_opt,self.longName]
        subprocess.run(scr_cmd)
        sys.exit()


class Screens():
    def __init__(self, sessions=[], args=None, config=None):
        self.args = args if args else {'nocolor':Fasle,}
        self._sessions = []
        self.sessions = sessions
        self.mergeActive()
        self.color = False if args['nocolor'] else True
        self.config = config if config else Config(args=args)
        self._log = self.config.log

    def __iter__(self):
        return ScreenIterator(self.sessions)

    def __str__(self):
        return f"{[str(s) for s in self]}"
    def __repr__(self):
        return f"<Screens {[str(s) for s in self]}"

    @classmethod
    def from_strings(cls, items, args=DEFAULT_CONFIG):
        """Create Screens instance from string or list of strings representing session names."""
        if isinstance(items, str):
            return cls([Screen(name=items)], args=args)
        elif isinstance(items, list):
            if all(isinstance(i, str) for i in items):
                return cls([Screen(name=i) for i in items], args=args)
        raise TypeError("Items added by <Screen>.from_string must be strings.")

    def runningScreens(self):
        """Get all currently running GNU Screen sessions by parsing 'screen -ls' output."""
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
        """Merge running screen sessions with configured defaults, updating PIDs and states."""
        for ses in self.runningScreens():
            found = False
            for ds in self.sessions:
                if ds.name == ses.name and not ds.pid:
                    ds.pid = int(ses.pid)
                    ds.state = ses.state
                    found = True
                    break
            if not found:
                self.sessions.append(ses)
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
                         "<Screens>.sessions all have to be of type <Screen>")
        else:
           raise TypeError(
             "<Screen>.sessions must be <Screen> or list of <Screen> objects.")
        self._sessions = _new_sessions

    def append(self, item):
        """Add a Screen object to the sessions list."""
        if isinstance(item, Screen):
            self._sessions.append(item)
        else:
            raise TypeError("<Screen>.screens items must <Screen> objects.>")

    def createMenu(self, show=False):
        m = ScrDisplay("Screen Session Menu",[],config=self.config)
        for idx, screen in enumerate(self.sessions, start=1):
            detail = ''
            if screen.is_active:
                detail = f"{screen.longName: <15} {screen.state}"
            m.addMenuOption(f"{screen.name: <10} {detail}", screen, idx)
        m.addMenuControl("New Screen Session",None,"N")
        m.addMenuControl("Refresh Menu",None,"R")
        m.addMenuControl("EXIT",None,"E")
        m.showMenu()
        return m

    def displayMenu(self):
        """
          Display interactive menu for selecting, creating, 
          or attaching to screen sessions.
        """
        log = self.log
        menu = self.createMenu(show=True)
        while True:
            choice = menu.getMenuChoice().lower()
            if choice == "e":
                sys.exit(0)
            elif choice == 'r':
                menu.showMenu()
            elif choice == 'n': # create a new screen
                new_name = menu.getString()
                if not all(c.isalpha() or c =='_' for c in new_name):
                    log.error("[[R]]Screen can only be letters or _ [[E]]")
                    continue
                if not new_name:
                    log.error("[[R]]Empty screen name not allowed.[[E]]\n")
                    continue
                else:
                    new_screen = Screen(name=new_name)
                    new_screen.run()
            try:
                ch = int(choice)
            except:
                continue
            if ch not in [c.menu_char for c in s.options]:
                continue
            else:
                [c.action for c in s.options if ch==c.menu_char][0].run()

