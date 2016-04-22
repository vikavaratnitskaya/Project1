from utils import *
from local_operations import *
from remote_operations import *
from commands_parser import *
from ssh_connect import *

def file_copy(args, ids, ssh):
    local_info_dict = {}
    local_files = find_local_files(args.lpath, "f")
    md5 = ""
    for local_file in local_files:
        md5 = local_md5_check(local_file)
        if md5 not in local_info_dict.keys():
            local_info_dict[md5] = {"name" : local_file}

    remote_info_dict = {}
    remote_files = find_remote_files(ids["path"], "f", ssh)
    md5 = ""
    for remote_file in remote_files:
        md5 = remote_md5_check(remote_file, ssh)
        if md5 not in remote_info_dict.keys():
            remote_info_dict[md5] = {"name" : local_file}
    hashes_to_copy = set(local_info_dict.keys()) - set(remote_info_dict.keys())

    files_to_copy = []
    for hash_to_copy in hashes_to_copy:
        files_to_copy.append(local_info_dict[hash_to_copy]["name"]) 
    
    rsync_dest = ""
    stdin, stdout, stderr = ssh.exec_command("which rsync")
    local_dirs = find_local_files(args.lpath, "d")
    for line in stdout:
        rsync_dest = line.rstrip()
    for local_dir in local_dirs:
        relative_path = re.sub(args.lpath, "", local_dir)
        remote_make_dir("".join((ids["path"], relative_path)), ssh)
    
    for file_to_copy in files_to_copy:
        relative_path = re.sub(args.lpath, "", file_to_copy)
        destination = "".join((args.rpath, relative_path))
        command = "rsync --rsync-path=%s %s -%s %s" % (rsync_dest, file_to_copy, args.rsync, destination) 
        process = subprocess.call(command, shell = True)

def main():
    check_os()
    args = verify_arguments(sys.argv)
    ids = splitter(args)
    if host_is_pingable(ids["host"]) and ssh_available(ids["host"]):
        ssh = ssh_open(args, ids)
        file_copy(args, ids, ssh)
        ssh_close(ssh)

if __name__ == "__main__":
    main()
