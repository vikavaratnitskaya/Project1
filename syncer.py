from utils import *
from local_operations import *
from remote_operations import *
from commands_parser import *
from ssh_connect import *

def file_dictionary_constructor(args, ids, ssh, machine):
    info_dict = {}
    if machine == "local":
	files = find_local_files(args.lpath, "f")
    else: 
	files = find_remote_files(ids["path"], "f", ssh)
    md5 = ""
    for f in files:
	if machine == "local":
            md5 = local_md5_check(f)
	else: 
            md5 = remote_md5_check(f, ssh)
        if md5 not in info_dict.keys():
            info_dict[md5] = {"name" : f}
    return info_dict
	
def file_copy(args, ids, ssh):
    if util_finder("rsync", ssh):
        local_info_dict = file_dictionary_constructor(args, ids, ssh, "local")
        remote_info_dict = file_dictionary_constructor(args, ids, ssh, "remote")
        hashes_to_copy = set(local_info_dict.keys()) - set(remote_info_dict.keys())
        files_to_copy = []
        for hash_to_copy in hashes_to_copy:
            files_to_copy.append(local_info_dict[hash_to_copy]["name"]) 
        remote_make_dir(ids["path"], ssh)
        local_dirs = find_local_files(args.lpath, "d")
        for local_dir in local_dirs:
            relative_path = re.sub(args.lpath, "", local_dir)
            remote_make_dir("".join((ids["path"], relative_path)), ssh)
    
        for file_to_copy in files_to_copy:
            relative_path = re.sub(args.lpath, "", file_to_copy)
            destination = "".join((args.rpath, relative_path))
            command = "rsync --rsync-path=%s %s -%s %s" % (util_finder("rsync", ssh), file_to_copy, args.rsync, destination) 
            process = subprocess.call(command, shell = True)
    else: print "Rsync is not found on %s" % ids["host"]
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
