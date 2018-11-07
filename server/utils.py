"""
This module contains helper functions to be utilized by the C2.
"""
# pylint: disable=global-statement
import json
import requests
from time import strftime, gmtime

from .config import SLACK_KEY_FILE, SLACK_CHANNEL, LOGFILE

SLACK_TOKEN = None


def _error_response(status, error_type, description):
    """
    Formats an error response.
    """
    return {
        'status': status,
        'error_type': error_type,
        'description': description,
        'error': True,
    }

def log(msg, level='DEBUG'):
    """
    Log a message.
    """
    # Log the output and save the hostname
    log_line = "{} {}".format(strftime("%H:%M:%S", gmtime()), msg)
    try:
        with open(LOGFILE, "a") as logfil:
            logfil.write(log_line+"\n")
    except Exception as E:
        print("Cannot write to", LOGFILE)

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
        req = requests.post(host, json=data, timeout=1)
        return True
    except Exception as E:
        slackError("Cannot update pwnboard: {}".format(E))
        return False
