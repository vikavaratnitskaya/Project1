import argparse
import paramiko
import os
import sys
import re
import hashlib
import subprocess
import logging

def verify_arguments(argv): # argv is not used - why?
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
    parser.add_argument("-loglevel", dest='loglevel', action="store",
                        default='DEBUG',
                        choices={'DEBUG', 'INFO', 'WARN', 'ERROR'},
                        help="Set logging level")
    parser.add_argument("-logpath", dest='logpath', action="store",
                    default='/tmp/logs.log', help="Define logging file path")
    args = parser.parse_args()
    return args

# The isolation of elements to transfer (host,port,user,path) without "password"
def splitter(args, log):
    string = args.rpath
    port = None
    strUsrHst = string.split("@")
    usrPrt = strUsrHst[0] # What do usrPrt and strUsrHst mean? 
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
        intPort = int(port) # Will I crash if I'll mistype port as '22p' for example? We can handle this, I believe.
        # Any inappropriate usernames - emprty usernames, how will we treat them?
        if 1 > intPort or intPort > 65535:
            print "Invalid number of port! The port will be set by default." # Print is OK, how about logginhg?
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
            print "Invalid number of port! The port will be set by default." # Print is OK, how about logginhg?
            port = 22
    hstPth = strUsrHst[1].split(':')
    #for logging
    source_ip = socket.gethostbyname(socket.gethostname())

    host = hstPth[0]
    log.info("%s to %s" % (source_ip, host))
    if len(hstPth)==2:
        path = hstPth[1]
    else: path = "/home/"+user+"/"
    ids = [host, user, path, port]
    return ids

def ssh_open(args, ids, log):
    while True:
        print "Try to connect to %s" % ids[0]
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if args.pas == None:
                client.connect(hostname=ids[0], username=ids[1])
            else:
                client.connect(hostname=ids[0], username=ids[1], password=args.pas)
            print "Connected to %s" % ids[0]
            break
        except paramiko.AuthenticationException:
            log.error("Authentication failed when "
                      "connecting to %s" % ids[0])
        raise
        return client # Is this part of code ever reachable?

def ssh_close(client, log): # SSH life cycle can be treated with try-except or with context.
    # It can and should be treated in a separate namespace (function/class/package)
    client.close()
    log.info("ssh conection is closed")
    
def dir_exists_check(directory, ssh, log):
    sftp = ssh.open_sftp()
    try:
        sftp.stat(directory)
    except IOError, e:
        if e[0] == 2:
            log.error("Checking file existance failed with %s" % e[0])
            return False
        raise
    else:
        return True
    
def remote_make_dir(directory, ssh):
    if not dir_exists_check(directory, ssh, log):
        ssh.exec_command("mkdir %s" % directory)

def find_remote_files(remote_path, t, ssh): # When you will need other SSH command to be executed, you'll need to copypaste the code
    remote_files = []
    stdin, stdout, stderr= ssh.exec_command(
        "find %s -name \"*\" -type %s" % (remote_path, t))
    for f in stdout.readlines():
        remote_files.append(str(f.rstrip()))
    return remote_files

def find_local_files(path, t, log):
    log.info("Finfing local files started")
    local_dirs = []
    local_files = []
    for target_folder, subdirs, filenames in os.walk(path):
        for subdir in subdirs:
        	local_dirs.append(os.path.join(target_folder, subdir))
        for filename in filenames:
        	local_files.append(os.path.join(target_folder, filename))
    if t == "f":
    	return local_files
    if t == "d":
    	return local_dirs
    log.info("Finfing local files started")


def local_md5_check(f, log): # When you will need other shell command to be executed, you'll need to copypaste the code
    log.info("md5 function started")
    target = "md5sum %s" % f
    local_out = subprocess.Popen(target, shell = True,
        stdout = subprocess.PIPE)
    checksum = local_out.communicate()[0]
    local_checksum = checksum.split(" ")[0]
    return local_checksum
    log.info("md5 function finished") # Is this part of code ever reachable?


def remote_md5_check(f, ssh):# When you will need other SSH command to be executed, you'll need to copypaste the code 
    stdin, stdout, stderr = ssh.exec_command("/usr/bin/md5sum %s" % f) # How would you treat stderr? What if STDOUT is empty?
    remote_checksum = None
    for line in stdout.readlines():
        remote_checksum = line.split(" ")[0]
    return remote_checksum

def file_copy(args, ids, ssh, log):
    log.info("Copying files started")
    local_files = find_local_files(args.lpath, "f", log)
    local_dirs = find_local_files(args.lpath, "d", log)
    remote_files = find_remote_files(ids[2], "f", ssh)
    log.info("Copying files finished")
    
    
    ## md5 check to be added THIS DOESNT WORK OR does?
    final_source =  local_files
    for lfile in local_files:
        for rfile in remote_files:
            if local_md5_check(lfile, log) == remote_md5_check(rfile, ssh):
                if lfile in final_source:
                    final_source.remove(lfile)
           
    for local_dir in local_dirs:
        relative_path = re.sub(args.lpath, "", local_dir)
        remote_make_dir("".join((ids[2], relative_path)), ssh)
    for files in final_source:
        relative_path = re.sub(args.lpath, "", files)
        destination = "".join((args.rpath, relative_path))
        os.system("rsync --rsync-path=/usr/bin/rsync %s -%s %s" # Hardcoded path - what if rsync exists in another place?
                   % (files, args.rsync, destination))
        code = os.system("rsync --rsync-path=/usr/bin/rsync" # Hardcoded path - what if rsync exists in another place?
                         " --checksum %s -%s %s"
                         % (args.lpath, args.rsync, merge_path))
        # And in general - why there is no check for stdout and stderr?
        # Why use different run approaches running local shell commands?
        if code > 0:
            log.error("rsync fails with error code %s" % code)
            sys.exit(1)
        #..to be continue..#


def main():
    args = verify_arguments(sys.argv)
    logging.basicConfig(
        filename=args.logpath,
        level=getattr(logging, args.loglevel),
        format='%(levelname)s - %(asctime)s - %(message)s')
    log = logging.getLogger(__name__)
    log.info("Script Started")
    ids = splitter(args, log)
    ssh = ssh_open(args, ids, log)
    file_copy(args, ids, ssh, log)
    ssh_close(ssh, log)
    log.info("Script Finished")

if __name__ == "__main__":
    main()

