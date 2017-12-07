
from flask import Flask, request, jsonify, render_template
import dflib, json, os, threading, time

app = Flask('__name__')
db = dflib.Database()
sensorList = {}

@app.route('/events',methods=['GET','POST'])
def receive_events():
        raw_data = request.get_data()
        json_data = json.loads(raw_data)
        print(json_data)
        db.write_row(json_data)
        return '{"status": 200}\n'


@app.route('/get-id',methods=['GET','POST'])
def get_id():
    new_id = db.add_sensor()
    id_dict = {'id':new_id}
    return jsonify(id_dict)

@app.route('/db-view')
def frontend():
    return render_template('tableview.html', df=db.dataframe)

@app.route('/heartbeats',methods=['GET','POST'])
def get_heartbeat():
    all_args = request.args
    sensorList[all_args['id']] = True
    return '{"status": 200}\n'

def write_event(sensor_id, path, event, process):
    db.write_raw_data(sensor_id, path, event, process)

def run_heartbeat():
    while True :
        keys_to_remove = []
        for key,value in sensorList.items():
            if value == False :
                sensor_path = db.get_path_by_id(key)
                write_event(key, sensor_path, 'SENSOR_KILLED', 'SENSOR_INTERNAL_PROCESS')
                keys_to_remove.append(key)
            sensorList[key] = False
        for key in keys_to_remove:
            sensorList.pop(key, None)
        time.sleep(120)

heartbeatListener = threading.Thread(target=run_heartbeat)
heartbeatListener.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8080)
