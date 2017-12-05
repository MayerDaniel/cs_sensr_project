import pandas as pd
import os.path
import datetime
import pickle

def save_obj(obj, name):
    with open(name + '.pickle', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open(name + '.pickle', 'rb') as f:
        return pickle.load(f)

class Database:

    def __init__(self):
        columns = ['Sensor ID', 'Time', 'Path', 'Event', 'Process']
        if os.path.exists("df.pickle") :
            saved_df = load_obj("df")
            self.dataframe = saved_df.dataframe
            self.last_save = saved_df.last_save

        else :
            self.dataframe = pd.DataFrame(columns=columns)
            self.last_save = datetime.datetime.now()
            save_obj(self, "df")

    def add_sensor(self):
        currentIDs = self.dataframe['Sensor ID']
        new_id = 0
        if len(currentIDs.index) != 0:
            new_id = currentIDs.max() + 1
        return new_id

    def write_row(self, json):
        self.dataframe.append([json['id'], json['time'], json['path'], json['event'], json['process']])
        print(self.dataframe.head())
        self.check_save()

    def check_save(self):
        curr_time = datetime.datetime.now()
        difference = curr_time - self.last_save
        if difference.total_seconds() > 1:
            print("Database Saved")
            self.last_save = curr_time
            save_obj(self, "df")
