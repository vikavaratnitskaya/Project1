import os
import subprocess

def find_local_files(path, type_needed):
    local_dirs = []
    local_files = []
    for target_folder, subdirs, filenames in os.walk(path):
        for subdir in subdirs:
        	local_dirs.append(os.path.join(target_folder, subdir))
        for filename in filenames:
        	local_files.append(os.path.join(target_folder, filename))
    if type_needed == "f":
    	return local_files
    if type_needed == "d":
    	return local_dirs

def local_md5_check(f):
    target = "md5sum %s" % f
    local_out = subprocess.Popen(target, shell = True,
        stdout = subprocess.PIPE)
    checksum = local_out.communicate()[0]
    local_checksum = checksum.split(" ")[0]
    return local_checksum
