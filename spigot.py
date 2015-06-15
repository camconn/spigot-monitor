
# (c) Copyright Cameron Conn 2015
# Licensed AGPLv3 or Later
# See `LICENSE` for full details

"""
Module to assist parsing and using output gathered from Spigot.

Also helps with data management.
"""

from time import strftime, sleep
from os import kill, getpid
from signal import SIGTERM
from enum import Enum
from wrapper import SpigotData
#import yaml  # for reading/writing config


# CLASSES #################################################

class SpigotState(Enum):
    """
    Enums for server status

    status - Bitmask for status of server
        STOPPED - server is stopped
        STARTING - server is booting up, but not ready
        RUNNING - server has sent `DONE` message
    """
    STOPPED = 0
    STARTING = 1
    RUNNING = 2


class DiagData:
    """
    Class to hold server diagnostic data
    """
    def __init__(self):
        self.startup_time = 0


class GameData:
    """
    Class to hold game data
    """
    def __init__(self):
        self.players = []
        self.status = SpigotState.RUNNING


# METHODS #################################################

def parse_event(sd: SpigotData, line):
    """
    Parse an event from console log and act accordingly.
    """
    words = line.split(' ')

    l_words = tuple(word.lower() for word in words)

    first_word = l_words[2]
    sec_word = l_words[3]
    nwords = len(words)

    if '<' in first_word and '>' in first_word:  # Chat
        return

    if first_word == 'done':
        done_time = float(words[3][1:-3])
        print('statup time is {} seconds'.format(done_time))
        sd.diag.startup_time = done_time
    elif sec_word == 'logged':
        player = words[2].split('[')[0]
        print('{} joined the game'.format(player))
        sd.game.players.append(player)
    elif sec_word == 'left':
        # check that `<` isn't in name because angle brackets
        # indicate chat

        player = words[2]
        print('{} left the game'.format(player))
        sd.game.players.remove(player)

    # TODO: Temporary KeyError fix when less than 5 words
    if nwords < 5:
        return

    if words[3] == 'fell':
        print('{} died from heights'.format(words[2]))
        return
    elif words[4] == 'blown':
        print('{} was blown up by {}'.format(words[2], words[7]))
        return
    elif words[4] == 'slain':
        print('{} was slain by {}'.format(words[2], words[6]))
        return


def info_message(message: str) -> str:
    """
    Create an informational message to write to scrollback

    message - message to append an info prefix to
    """
    time_fmt = strftime('%H:%M:%S')

    return '[{} SPIGOT-MONITOR] {}'.format(time_fmt, message)


def command_handler(sd: SpigotData, command):
    """
    Handle commands and whether they're internal to Spigot Monitor
    or external to Spigot itself.
    """
    command_lower = command.lower()

    with sd.lock:
        sd.add_message('> {}'.format(command))

    if command_lower == 'clear':
        sd.scrollback.clear()
        return
    elif command_lower == 'quit-all':
        print('quitting all')
        sd.commands.put('stop\n')

        # wait until r_w_worker Thread is dead
        print('sent stop command')
        sd.close_event.wait()
        print('stopped. sending quit command.')
        sleep(1)  # wait, just in case
        sd.commands.put('quit\n')  # now it's time for data_handler to die

        # seppuku
        print('stopping everythang')
        kill(getpid(), SIGTERM)
        return  # just to be correct
    elif command_lower == 'list' or command_lower == 'who':
        # We do this ourselves
        # Be long-winded to get plurality right
        num = len(sd.game.players)
        if num == 0:
            sd.add_message(info_message('There are no players online.   :-('))
            return
        elif num == 1:
            sd.add_message(info_message('There is 1 player online:'))
            sd.add_message(sd.game.players[0])
        else:
            sd.add_message(info_message('There are {} players online:'.format(num)))
            sd.add_message(', '.join(sd.game.players))
        sd.add_message('End of players list.')
        return
    else:
        sd.commands.put('{}\n'.format(command))
        return
