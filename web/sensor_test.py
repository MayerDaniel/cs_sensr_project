'''
Mini sensor created for CrowdStrike externship
Created by Tyler Chang and Daniel Mayer
'''
import requests, pickle, os.path, os
import subprocess, time, threading, sched
from datetime import datetime, timezone

#TODO add ID for sensor
#TODO send get requests



class File_monitor:
    def __init__(self):
        self.watchlist = []
        self.get_id()

    '''
    Creates a timestamp in our desired format
    '''
    def get_time(self, system_time):
        timestamp = datetime.strptime(system_time, "b\'%H:%M:%S.%f")
        today = datetime.now()
        timestamp = timestamp.replace(year=today.year, month=today.month, day=today.day)
        timestamp = timestamp.astimezone(timezone.utc)
        timestamp = timestamp.replace(microsecond= (int)(timestamp.microsecond/10000)*10000)
        return timestamp


    '''
    checks to see if the sensor has already been assigned an id, if not,
    queries the cloud for a new one
    '''
    def get_id(self):
        if os.path.exists("SensorData/id.pickle") :
            f = open("SensorData/id.pickle","r+b")
            self.id = pickle.load(f)
            self.send_event(datetime.now(timezone.utc), os.path.realpath(__file__),
                'SENSOR_RESTARTED', 'SENSOR_INTERNAL_PROCESS')
        else :
            if not os.path.exists("SensorData") :
                os.makedirs("SensorData")
            f = open("SensorData/id.pickle","wb")
            response = requests.get("http://localhost:8080/get-id").json()
            sensor_id = response['id']
            pickle.dump(sensor_id, f)
            f.close()
            self.id = sensor_id
            self.send_event(datetime.now(timezone.utc), os.path.realpath(__file__),
                'SENSOR_CREATED', 'SENSOR_INTERNAL_PROCESS')

    '''
    constructs event and sends it to a desired endpoint
    '''
    def send_event(self, time, path, event, process, endpoint='events'):
        event_data = {}
        event_data['id'] = self.id
        event_data['time'] = str(time)
        event_data['path'] = path
        event_data['event'] = event
        event_data['process'] = process
        r = requests.post("http://localhost:8080/" + endpoint, json=event_data)

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
                        timestamp = self.get_time(split[0])
                        if timestamp != lastTimestamp : #maybe put more logic here?
                            lastTimestamp = timestamp
                            self.send_event(timestamp, split[4], split[1], split[6])


    def prompt(self):
        while True:
            file_or_dir = input("Enter any directory or file to watch: ")
            self.add_to_watchlist(file_or_dir)
            print("Added to watch list! If you have another file add below.")


    '''
    Sends a get request every 60 seconds
    '''
    def heartbeat(self):
        while True:
            r = requests.get("http://localhost:8080/heartbeats?id=" + str(self.id))
            time.sleep(60)


'''
Creates a CLI to interact with sensor and add to watchlist
'''
def main():
    threads = []
    f = File_monitor()
    print(f.id)
    p = threading.Thread(target=f.prompt)
    threads.append(p)
    t = threading.Thread(target=f.watch)
    threads.append(t)
    h = threading.Thread(target=f.heartbeat)
    threads.append(h)
    for thread in threads :
        thread.start()


if __name__ == "__main__":
    main()
