#filters output

import subprocess
proc = subprocess.Popen(['fs_usage', '-w'],stdout=subprocess.PIPE)
while True:
    line = str(proc.stdout.readline())
    if "testfile.txt" in line:
    #the real code does filtering here
        print(line.rstrip())
    else:
        pass
