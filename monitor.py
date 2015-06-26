#!/usr/bin/env python3

# Copyright (c) Cameron Conn 2015
# Licensed under AGPLv3 or Later
# See `LICENSE` for full details

import subprocess
from multiprocessing import Process, Pipe
import multiprocessing
import threading  # Used for bottle & main
import selectors
import psutil
import shlex
import bottle
import time
import os
from spigot import info_message, parse_event, SpigotState
from wrapper import SpigotWrapperPlugin, SpigotData
import webapp
import logging


#TODO: Load from config
AUTO_RESTART = True


def setup_process():
    # Use --nojline because jline breaks this script
    command_raw = 'java -jar spigot.jar nogui --nojline'
    command = shlex.split(command_raw)
    p = subprocess.Popen(command, stdin=subprocess.PIPE, universal_newlines=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p


def r_w_worker(worker_pipe, close_event):
    """
    Thread worker for reading and writing input from Java process

    worker_pipe - Pipe object to communicate with main thread with.
    close_event - multiprocessing.Signal to show that we're exiting.
    """
    os.chdir('spigot')

    close_event.clear()  # In case we've previously been closed
    process = setup_process()

    sel = selectors.DefaultSelector()
    sel.register(process.stdout, selectors.EVENT_READ)
    sel.register(process.stderr, selectors.EVENT_READ)
    sel.register(worker_pipe, selectors.EVENT_READ)

    pro = psutil.Process(process.pid)
    print('PID: {}'.format(process.pid))

    time.sleep(5)  # Hack to avoid race condition

    while pro.status() != 'zombie':
        events = sel.select()

        for k, e in events:
            if type(k.fileobj) is multiprocessing.connection.Connection:
                buf = k.fileobj.recv()
                print(buf, file=process.stdin, flush=True)
            else:
                s_buf = k.fileobj.readline()

                for line in s_buf.split('\n'):
                    if len(line) >= 1:  # TODO: Is this line even needed?
                        worker_pipe.send(line)
    # signal that we're closing shop
    close_event.set()


def data_handler(spigot_data: SpigotData, lock: threading.Lock):
    """
    Main thread for reading output from spigot IO worker.
    Also interprets data.

    spigot_data - shared SpigotData object
    """
    client, child = Pipe()

    t = Process(target=r_w_worker, args=(child, spigot_data.close_event))
    t.start()

    spigot_data.game.status = SpigotState.RUNNING

    running = True

    while running:
        while t.is_alive():
            if client.poll(0.3):
                buf = client.recv()
                parse_event(spigot_data, buf)
                spigot_data.add_message(buf)
                logging.debug('<<OUTPUT>> {}'.format(buf))

            while not spigot_data.commands.empty():
                command = spigot_data.commands.get()
                client.send(command)
                logging.debug('<<COMMAND>> {}'.format(command))

        # After java process is dead
        spigot_data.status = SpigotState.STOPPED
        spigot_data.add_message(info_message("""The server has stopped. Type 'start' to start. """
                                             """Type 'quit' to close Spigot Monitor"""))  # PEP8ers gonna hate

        spigot_data.game.players = {}  # No players are available on a stopped server...

        while True and not AUTO_RESTART:
            command = spigot_data.commands.get().strip()  # strip because commands have newline appended
            if command.lower() == 'start':
                t = Process(target=r_w_worker, args=(child, spigot_data.close_event))
                t.start()
                logging.debug('Thread created.')
                break
            elif command.lower() == 'quit' or command.lower() == 'stop':
                message = info_message("KTHXBAI")
                spigot_data.add_message(message)
                logging.debug('Quitting program.')
                break

        if AUTO_RESTART:
            t = Process(target=r_w_worker, args=(child, spigot_data.close_event))
            t.start()
            logging.debug('Thread created.')

        if not t.is_alive():  # thread hasn't started again
            running = False

    print('exiting data_handler loop')


def bottle_setup(spigot_data: SpigotData):
    """
    Setup bottle with plugins and appropriate functions.

    spigot_data - SpigotData object for communicating and sharing
        data with main thread
    """
    b = bottle.Bottle()

    b.install(SpigotWrapperPlugin(spigot_data=spigot_data))

    bottle_app = webapp.setup(b)

    return bottle_app


def main():
    """
    Main function that does stuff
    """
    logging.basicConfig(filename='logs/monitor.log', level=logging.DEBUG)

    if not os.path.exists('spigot'):
        os.mkdir('spigot')
        print("""I made a `spigot` directory in this folder. """
              """Please place spigot.jar in it and run monitor.py again.""")
        logging.debug('No spigot directory found. I made one instead.')
        exit(-1)

    if not os.path.exists('spigot/spigot.jar'):
        print("""spigot.jar not found! Exiting.""")
        logging.debug('No spigot jarfile found.')
        exit(-2)

    spigot_data = SpigotData()

    scrollback_lock = threading.Lock()
    m_thread = threading.Thread(target=data_handler, args=(spigot_data, scrollback_lock))

    m_thread.start()

    web = bottle_setup(spigot_data)
    web.run(host='0.0.0.0', port=25564, quiet=True)
    #web.run(host='127.0.0.1', port=25564)

    m_thread.join()
    print('Stopping spigot-monitor')


if __name__ == '__main__':
    main()
