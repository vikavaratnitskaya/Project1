import paramiko

def ssh_open(args, ids):
    while True:
        print "Try to connect to %s" % ids["host"]
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if args.pas == None:
                client.connect(hostname=ids["host"], username=ids["user"])
            else:
                client.connect(hostname=ids["host"], username=ids["user"], 
				password=args.pas)
            print "Connected to %s" % ids["host"]
            break
        except paramiko.AuthenticationException:
            print "Authentication failed when connecting to %s" % ids[0]
            sys.exit(1)
        
            
    return client

def ssh_close(client):
    client.close()
