
# (c) Copyright Cameron Conn 2015
# Licensed AGPLv3 or Later
# See `LICENSE` for full details

"""
Module for Wrapper plugin for bottle.
"""

from collections import deque
from itertools import islice
from queue import Queue
from threading import Lock
from multiprocessing import Event
import spigot
#from spigot import DiagData, GameData


class SpigotData:
    """
    Object to hold information about Spigot.

    close_event - Event signaled on end of multiprocessing thread,
        which allows Spigot Monitor to exit
    commands - Queue of commands sent from bottle to Java
    status - SpigotState enum for what state the server is in. Defaults
        to SpigotState.RUNNING
    lock - Thread lock object
    static_dir - location of templates and static files for web UI
    msg_num - Message number of scrollback (for updating web UI
        without a page reload)
    diag - Diagnostic data stored in DiagData object
    game - Diagnostic data stored in GameData object
    """

    def __init__(self):
        """
        static_dir - directory where bottle templates, CSS, etc. are located
        """
        self.status = 0
        self.diag = spigot.DiagData()
        self.game = spigot.GameData()
        self.scrollback = deque(maxlen=512)
        self.msg_num = 0
        self.close_event = Event()
        self.commands = Queue()
        self.lock = Lock()

    def add_message(self, message: str):
        """
        Add a message to scrollback, and increase message cout

        message - message to add to scrollback
        """
        self.scrollback.append(message)
        self.msg_num += 1

    def clearscrollback(self):
        """
        Clear scrollback completely by emptying it.
        """
        self.scrollback.clear()
        self.msg_num = 0

    def scrollback_since(self, msg_id: int) -> tuple:
        """
        Get scrollback messages since a message.

        Returns a tuple of messages since a message id.
        Returns None if no new messages

        msg_id - last message id received (exluded from output)
        """
        if msg_id == self.msg_num:
            return None

        id_first_msg = 0

        if self.msg_num > self.scrollback.maxlen:
            id_first_msg = self.msg_num - self.scrollback.maxlen

        cutoff_index = msg_id - id_first_msg + 1

        return islice(self.scrollback, cutoff_index, None)


class SpigotWrapperPlugin(object):
    """
    Plugin for bottle that allows bottle to display scrollback
    and send commands to spigot/craftbukkit server.
    """

    name = 'spigotwrapper'
    api = 2

    def __init__(self, spigot_data: SpigotData, keyword='sw'):
        self.sd = spigot_data
        self.keyword = keyword

    def setup(self, app):
        """
        Make sure we don't conflict with anything else
        """
        pass

    def apply(self, callback, route):
        """
        Method to apply bottle plugin
        """

        def wrapper(*args, **kwargs):
            """Wrapper decorator"""

            sd = self.sd

            return callback(sd, *args, **kwargs)
        return wrapper

Plugin = SpigotWrapperPlugin
