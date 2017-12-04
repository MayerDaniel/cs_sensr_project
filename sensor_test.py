'''
Mini sensor created for CrowdStrike externship
Created by Tyler Chang and Daniel Mayer
'''
import requests, pickle, os.path
import subprocess, time, threading
from datetime import datetime, timezone

#TODO add ID for sensor
#TODO send get requests

class File_monitor:
    def __init__(self):
        self.watchlist = []
        # self.id = self.get_id()

    '''
    '''
    # def get_id(self):
    #     if os.path.exists("SensorData/id.pickle") :
    #         return pickle.load("SensorData/id.pickle")
    #     else :
    #         if not os.path.exists("SensorData") :
    #             os.makedirs("SensorData")
    #         f = open("SensorData/id.pickle","w")
    #         a = 1
    #         pickle.dump(a, f)
    #         f.close()
    #         return 1
        #     return requests.get("http://localhost:8080/get-id")


    '''
    adds a new file or directory to the watchlist so that
    you do not create multiple subprocesses that are
    running the same command
    '''
    def add_to_watchlist(self, file_or_dir_to_add):
        self.watchlist.append(file_or_dir_to_add)

    '''
    calls the subprocess in OSX system internals that monitors disk
    activity events, and filters them based off of our watchlist
    '''
    def watch(self):
        proc = subprocess.Popen(['fs_usage', '-w'],stdout=subprocess.PIPE)
        lastTimestamp = 0
        while True:
            line = str(proc.stdout.readline())
            for item in self.watchlist :
                event_data = {}
                if item in line:
                    split = line.rstrip().split()

                    #open
                    if split[1] == "open" :
                        #time
                        timestamp = datetime.strptime(split[0], "b\'%H:%M:%S.%f")
                        today = datetime.now()
                        timestamp = timestamp.replace(year=today.year, month=today.month, day=today.day)
                        timestamp = timestamp.astimezone(timezone.utc)
                        timestamp = timestamp.replace(microsecond= (int)(timestamp.microsecond/10000)*10000)
                        if timestamp != lastTimestamp : #maybe put more logic here?
                            lastTimestamp = timestamp
                            event_data['time'] = timestamp
                            event_data['path'] = split[4]
                            event_data['event'] = split[1]
                            event_data['process'] = split[6]
                            print(event_data)
                            r = requests.post("http://localhost:8080/", data=event_data)


    def prompt(self):
        while True:
            file_or_dir = input("Please enter the path of a file or directory you would like watched: ")
            self.add_to_watchlist(file_or_dir)

'''
Creates a CLI to interact with sensor and add to watchlist
'''
def main():
    threads = []
    f = File_monitor()
    p = threading.Thread(target=f.prompt)
    threads.append(p)
    p.start()
    t = threading.Thread(target=f.watch)
    threads.append(t)
    t.start()


if __name__ == "__main__":
    main()
