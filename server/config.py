"""
This module contains configuration information for the server.
"""
import os

SLACK_KEY_FILE = '/opt/arsenal-c2/.slack_key'
SLACK_CHANNEL = '#errors'
API_KEY_FILE = '/opt/arsenal-c2/.arsenal_key'
TEAMSERVER_URI = 'http://redteam-arsenal.com'
USE_ARSENAL = True
SERVER_ADDRESS = "misconfiguration.party"
BASE_DIR = "/etc/commands/"
if not os.path.exists(BASE_DIR):
    os.mkdir(BASE_DIR)
LOGFILE = BASE_DIR + "/server.log"

#SERVER_ADDRESS = None   # Set this to override the public lookup of the server IP.
                        #This is used to determine the initial URI that session is beaconing to.

LOG_LEVEL = 'DEBUG'     # Set this to the desired log level of the server.
                        # Log levels: DEBUG, INFO, WARN, CRIT, FATAL

