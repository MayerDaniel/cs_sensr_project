
from flask import Flask, request, jsonify, render_template
import dflib, json

app = Flask('__name__')
db = dflib.Database()


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


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8080)
