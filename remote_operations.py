def remote_dir_exists_check(directory, ssh):
    sftp = ssh.open_sftp()
    try:
        sftp.stat(directory)
    except IOError, e:
        if e[0] == 2:
            return False
        raise
    else:
        return True
    
def remote_make_dir(directory, ssh):
    if not dir_exists_check(directory, ssh):
        ssh.exec_command("mkdir %s" % directory)

def find_remote_files(remote_path, t, ssh):
    remote_files = []
    stdin, stdout, stderr= ssh.exec_command(
        "find %s -name \"*\" -type %s" % (remote_path, t))
    for f in stdout.readlines():
        remote_files.append(str(f.rstrip()))
    return remote_files

def remote_md5_check(f, ssh):
    stdin, stdout, stderr = ssh.exec_command("/usr/bin/md5sum %s" % f)
    remote_checksum = None
    for line in stdout.readlines():
        remote_checksum = line.split(" ")[0]
    return remote_checksum
