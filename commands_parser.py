import argparse
import re
import sys


def verify_arguments(argv):
    usage = "syncer.py -pas ssh_password lpath local_path \
        - rcync_arguments --file single_file_name remote_path"
    epilog = "Remote path should be specified as root@hostname:/folder"
    parser = argparse.ArgumentParser(description = "Remote copy utility",
        usage = usage, epilog = epilog)
    parser.add_argument("-lpath", action = "store",
        default = None, help = "Local path")
    parser.add_argument("-pas", action = "store",
        default = None, help = "SSH password")
    parser.add_argument("-", dest = "rsync", action = "store",
        default = None, help = "rsync options")
    parser.add_argument("-file", action = "store",
        default = None, help = "single file to copy")
    parser.add_argument("-rpath", action = "store",
        default = None, help = "Remote path")
    args = parser.parse_args()
    return args

# The isolation of elements to transfer (host,port,user,path) without "password"
def splitter(args):
    string = args.rpath
    port = None
    strUsrHst = string.split("@")
    usrPrt = strUsrHst[0]
    user = strUsrHst[0]
    a = re.search(',', usrPrt)
    if a is not None:
        elts = usrPrt.split(',')
        if elts[0].isalpha():
            user = elts[0]
            port = elts[1]
        else:
            user = elts[1]
            port = elts[0]
        intPort = int(port)
        if 1 > intPort or intPort > 65535:
            print "Invalid number of port! The port will be set by default."
            port = 22
    a = re.search(':', usrPrt)
    if a is not None:
        elts = usrPrt.split(':')
        if elts[0].isalpha():
            user = elts[0]
            port = elts[1]
        else:
            user = elts[1]
            port = elts[0]
        intPort = int(port)
        if 1 > intPort or intPort > 65535:
            print "Invalid number of port! The port will be set by default."
            port = 22
    hstPth = strUsrHst[1].split(':')
    host = hstPth[0]
    if len(hstPth)==2:
        path = hstPth[1]
    else: path = "/home/"+user+"/"
    ids = {}
    ids["host"] = host
    ids["user"] = user
    ids["path"] = path
    ids["port"] = port
		
    return ids
