"""
This module contains helper functions to be utilized by the C2.
"""
# pylint: disable=global-statement
import json
import time
import requests
from .config import SLACK_KEY_FILE, SLACK_CHANNEL

SLACK_TOKEN = None

SESSIONS = {}
RESPONSES = []


def error_response(status, error_type, description):
    """
    Formats an error response.
    """
    return {
        'status': status,
        'error_type': error_type,
        'description': description,
        'error': True,
    }

def add_action_ids(action_ids):
    '''
    Add the given action IDs to the response list
    '''
    global RESPONSES
    epoch = int(time.time())
    for action in action_ids:
        RESPONSES += [{
            'action_id': action,
            'stdout': '', 'stderr': '',
            'start_time': epoch, 'end_time': epoch,
            'error': False
        }]

def get_responses():
    '''
    Get all the stored up responses that we have and reset
    '''
    global RESPONSES
    retval = RESPONSES
    RESPONSES = []
    return retval

def add_session(addr, name, session_id):
    '''
    add the session id for the given ip and name
    '''
    global SESSIONS
    key = hash(addr+"/"+name)
    print("New sessions for ",key)
    SESSIONS[key] = session_id


def is_session(addr, name):
    '''
    Check if the ip and name is a session, if not, return an empty string
    '''
    key = hash(addr+"/"+name)
    if key in SESSIONS:
        print("old sessions for ",key)
        return SESSIONS.get(key)
    return ""

def log(msg, level='DEBUG'):
    """
    Log a message.
    """
    print('[{}]{}'.format(level, msg))

def public_ip():
    """
    This method returns the public facing ip address of the server.
    """
    return requests.get("http://ipecho.net/plain?").text


def getSlackKey():
    '''
    Read the slack API token from the config
    '''
    global SLACK_TOKEN
    try:
        with open(SLACK_KEY_FILE, 'r') as slkfil:
            SLACK_TOKEN = slkfil.read().strip()
        if SLACK_TOKEN is None or SLACK_TOKEN == "":
            raise Exception("Bad slack token")
        return True
    except Exception as E:
        return False


def sendSlackMsg(msg, force=False):
    '''
    Send a slack message to the appropriate channel
    '''
    # Get the slack token
    if SLACK_TOKEN is None:
        if not getSlackKey():
            print("Slack token missing")
            return False
    if msg == "":
        return False

    # Prepare the request data
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer '+SLACK_TOKEN}
    data = {'channel': SLACK_CHANNEL, 'text': msg, 'as_user': 'true'}
    host = "https://slack.com/api/chat.postMessage"
    try:
        req = requests.post(host, data=json.dumps(data), headers=headers)
        req = req.json()
        if req['ok']:
            return True
        else:
            return False
    except Exception as E:
        return False

def slackError(msg):
    return sendSlackMsg("<!channel> JOYFULNOISE: {}".format(msg))


def updatePwnboard(ip):
    host = "https://pwnboard.win/generic"
    data = {'ip': ip, 'type': "JOYFULNOISE"}
    try:
        req = requests.post(host, json=data, timeout=3)
        return True
    except Exception as E:
        slackError("Cannot update pwnboard: {}".format(E))
        return False
