from flask import Flask, request

app = Flask('__name__')

@app.route('/events',methods=['GET','POST'])
def receive_events():
    try:
        data = request.get_data()
        print(data)
    except:
        traceback.print_exc()
        return None, status.HTTP_500_INTERNAL_SERVER_ERROR

    return '{"status": 200}\n'


# @app.route('/get-id',methods=['GET','POST'])
# def receive_get_id():
#     return 1


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False,port=8080)
