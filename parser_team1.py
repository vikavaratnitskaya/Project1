# Project1
import re
import connect
import logging

USER_PORT_HOST_PATH = '^(\w+)[:\.,]*(\d+\w+)*@(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):*((?:\/\w+)+)*'
LOCAL_PATH = '^((?:\/\w+)+\**/*)'
SINGLE_FILE = '^(\w+\.\w{2,5})$'
PASSWORD = '^-pass=[\'"](.+)[\'"]$'
RSYNC_ATTRIBUTES = '^(-\w+)$'


def remote_machines(attributes):
    """
    Returns all valid remote machines with all of their attributes parsed.
    """
    valid_machines = []
    for item in attributes:
        remote_machine = {}
        machine = re.search(USER_PORT_HOST_PATH, item)
        secret = re.search(PASSWORD, item)
        if machine:
            remote_machine['user'] = machine.group(1)
            if machine.group(2):
                port = ''
                for i in machine.group(2):
                    if i.isdigit():
                        port += i
                remote_machine['port'] = int(port)
            else:
                remote_machine['port'] = 22
            remote_machine['host'] = machine.group(3)
            remote_machine['path'] = machine.group(4)
            remote_machine['password'] = secret
            try:
                ssh = connect.open_sshclient(host=remote_machine['host'], port=remote_machine['port'], \
                                            user=remote_machine['user'], secret=remote_machine['password'])
                if connect.remote_check(remote_machine['host'], ssh):
                    valid_machines.append(remote_machine)
                ssh.close()
            except:
                print'Can not establish ssh connection on host {}'.format(remote_machine['host'])
                logging.info('Can not establish ssh connection on host {}'.format(remote_machine['host']))
        else:
            pass
    return valid_machines


def single_files_parser(attributes):
    """
    Returns single files from arguments.
    """
    single_files = []
    for item in attributes:
        file = re.search(SINGLE_FILE, item)
        if file:
            single_file = file.group(1)
            single_files.append(single_file)
    if single_files:
        return single_files
    else:
        return None


def local_path_parser(attributes):
    """
    Returns local path from arguments.
    """
    local_path = ''
    for item in attributes:
        path = re.search(LOCAL_PATH, item)
        if path:
            local_path = path.group(1)
            break
    return local_path


def rsync_keys_parser(attributes):
    """
    Returns rsync attributes.
    """
    rsync_keys = []
    for item in attributes:
        rsync_key = re.search(RSYNC_ATTRIBUTES, item)
        if rsync_key:
            rsync_keys.append(rsync_key.group(1))
    return rsync_keys
