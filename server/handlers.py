"""
This module contains handlers that will deal with incoming connections.
"""
import os

from .config import BASE_DIR
from .utils import log
import shlex


def get_file_commands(ip, hostname):
    base = BASE_DIR
    if os.path.isfile(base+ip+".txt"):
        fil = base+ip+".txt"
    elif os.path.isfile(base+hostname+".txt"):
        fil = base+hostname+".txt"
    else:
        fil = base+"default.txt"

    # Log the output and save the hostname
    log_line = "\tHOST:{}\tRQST: {}\tRECV: {}".format(ip, hostname, fil)
    log(log_line)

    data = "# no commands\n"
    try:
        with open(fil) as f:
            data = f.read()
    except Exception as E:
        pass
    return data

