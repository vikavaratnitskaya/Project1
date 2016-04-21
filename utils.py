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
        print "ssh is running on", host
        return True
    else:
        print "ssh is not running on", host
        return False   

def host_is_pingable(host):
    command = "ping -c 3 %s" % host
    if subprocess.call(command, shell=True, stdout = open("/dev/null", "w"),
                stderr = s.STDOUT) == 0:
        print host, "is UP"
        return True
    else:
        print host, "is DOWN"
        return  False



    
