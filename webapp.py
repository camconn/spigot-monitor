
# (c) Copyright Cameron Conn 2015
# Licensed AGPLv3 or later
# See `LICENSE` for full details

"""
Functions to be attached to bottle object
"""

from bottle import template, Bottle, request, static_file, abort, response
from wrapper import SpigotData
from os.path import join
from time import sleep
import spigot
from json import dumps
from os import getcwd


def setup(app: Bottle):
    """
    Set up bottle web application
    """

    @app.post('/')
    @app.route('/')
    def frontpage(sd: SpigotData, **kwargs):
        """
        Root page for bottle.
        """
        data = dict()

        if request.method == 'POST':
            if 'command' in request.forms:
                command = request.forms['command'].strip()
                spigot.command_handler(sd, command)
                data['msg'] = 'Command sent!'
                # Temporary sleep to let command execute. Remove this
                # once websocket updates are implemented.
                sleep(1.5)
        data.update(kwargs)

        with sd.lock:
            sb_tuple = tuple(line for line in sd.scrollback)
            player_list = sd.game.players
            return make_page('frontpage.html', scrollback=sb_tuple, last_msg=sd.msg_num,
                             players=player_list)


    @app.route('/player/<player>')
    def player_page(sd: SpigotData, player):
        """
        Player information page
        """
        if player not in sd.game.players:
            abort(404, 'Player not found.')

        player_data = sd.game.players[player]

        return make_page('player.html', player=player, player_data=player_data)


    @app.route('/update-sb')
    def updated_scrollback(sd: SpigotData):
        """
        Send JSON object of messages since a certain message
        """
        # TODO: Possible bug - if you have enough uptime this will overflow
        # Not that it's a bad thing ;)
        message_id = request.query['msg']

        if not message_id:
            abort(400, 'You need to specify a message')

        try:
            message_id = int(message_id)
        except ValueError:
            abort(400, 'Bad message id, must specify an int')

        messages = sd.scrollback_since(message_id)

        if messages:
            return dumps(tuple(messages))
        else:
            response.status = 204  # No Content
            return None

    @app.route(path=('/<filepath>', '/static/<filepath:path>'))
    def serve_static(sd, filepath):
        return static_file(filepath, root='static/')

    def make_page(page_loc, **kwargs):
        """
        Page generation tool.
        """
        cwd = getcwd()
        page_loc = join(cwd, 'static', page_loc)
        page_top = join(cwd, 'static/header.html')
        page_bottom = join(cwd, 'static/footer.html')
        return template(page_loc, header=page_top, footer=page_bottom, **kwargs)

    return app
