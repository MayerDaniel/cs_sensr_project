from flask import Flask, request, jsonify
import dflib

app = Flask('__name__')
db = dflib.Database()


@app.route('/events',methods=['GET','POST'])
def receive_events():
    try:
        data = request.get_data()
        print(data)
    except:
        traceback.print_exc()
        return None, status.HTTP_500_INTERNAL_SERVER_ERROR

    return '{"status": 200}\n'


@app.route('/get-id',methods=['GET','POST'])
def get_id():
    new_id = db.add_sensor()
    id_dict = {'id':new_id}
    return jsonify(id_dict)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8080)
