from flask import Flask, request, jsonify
from pathlib import Path
import SSHConnect
import log_path
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "API's working!"

def get_logs(server_dict, log_path, find_text, body):

    # size = len( dict(body).items())
    start_date = change_date_format(body.get('date'))
    msisdn = body.get('msisdn')
    package_code = body.get('packageCode')
    status = body.get('status')

    res = {"response": []}
    cmd = f"cd {log_path} ; grep '{find_text}' *.csv | sort -k1,1r | head -n 1000 ;"
    for machine, server in server_dict.items():
        response_data = {"machine": '', "data": []}
        raw_data = SSHConnect.ssh_connect(
            host=server.get('host'), 
            username=server.get('user'),
            password=server.get('password'), 
            port=server.get('port'),
            command=cmd
        )
        for data in raw_data.split('\n'):
            if data:
                 if ((not msisdn or msisdn in data) and
                    (not package_code or package_code in data) and
                    (not status or status in data) and
                    (not start_date or start_date in data)):
                    response_data['data'].append(data)
        res['response'].append(response_data)
        response_data['machine'] = machine
    return res

def change_date_format(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        new_date_str = date_obj.strftime('%m/%d/%Y')
    except Exception as e:
        print(f"Error while parsing date format: {e}")
        return None
    return new_date_str

def get_what_to_find(obj):
    
    if obj.get('msisdn'):
        return obj.get('msisdn')
    elif obj.get('packageCode'):
        return obj.get('packageCode')
    elif obj.get('status'):
        return obj.get('status')
    elif obj.get('date'):
        return change_date_format(obj.get('date'))
    return

@app.route('/apis/dtac/getResponseLog', methods=['POST'])
def getResponseLogDTAC():
    body = request.get_json()
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.DTAC_SERVER, log_path.LOG_RESPONSE_PATH,first_to_find,body)
    return jsonify(res), 200

@app.route('/apis/dtac/getContactLog', methods=['POST'])
def getContactLogDTAC():
    body = request.get_json()
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.DTAC_SERVER, log_path.LOG_CONTACT_PATH,first_to_find, body)
    return jsonify(res), 200


@app.route('/apis/true/getResponseLog', methods=['POST'])
def getResponseLogTRUE():
    body = request.get_json()
  
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.TRUE_SERVER, log_path.LOG_RESPONSE_PATH, first_to_find, body)
    return jsonify(res), 200

@app.route('/apis/true/getContactLog', methods=['POST'])
def getContactLogTRUE():
    body = request.get_json()
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.TRUE_SERVER, log_path.LOG_CONTACT_PATH, first_to_find, body)
    return jsonify(res), 200


if __name__ == '__main__':
    app.run()