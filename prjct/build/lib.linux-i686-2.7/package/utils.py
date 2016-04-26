import platform
import subprocess
def check_os():
    if platform.system().lower() != "linux":
        print "The script you're trying to run is for Linux only"
        quit()

def ssh_available(host):
    command = "nmap %s" % host
    process = subprocess.check_output(command, shell = True)
    if "ssh" in process:
        return True
    else:
        print "ssh is not running on", host
        return False   

def host_is_pingable(host):
    command = "ping -c 2 %s" % host
    if subprocess.call(command, shell=True, 
	    stdout = open("/dev/null", "w"),
        stderr = subprocess.STDOUT) == 0:
        return True
    else:
        print host, "is DOWN"
        return  False

def util_finder(util, ssh):
    util_dest = ""
    stdin, stdout, stderr = ssh.exec_command("which %s" % util)
    for line in stdout:
        util_dest = line.rstrip()
    return util_dest



    
