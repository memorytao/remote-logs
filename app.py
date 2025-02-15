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


@app.route('/apis/dtac/getResponseLogs/<string:find_text>', methods=['GET'])
def get_response_dtac(find_text):

    res = {
        "response":[]
    }

    start_date = request.args.get('date')
    status = request.args.get('status')
    detail = request.args.get('find')

    cmd = f"cd {log_path.LOG_RESPONSE_PATH} ; grep {find_text} *.csv"
    for machine,server in log_path.DTAC_SERVER.items():
        response_data = {
            "machine":'',
            "data": None
        }
        raw_data = SSHConnect.ssh_connect(host=server.get('host'), username=server.get('user'),password=server.get('password'), port=server.get('port'),command=cmd)
        
        data = None
        if start_date:
            data = parse_data_format(raw_data,start_date)
        else:
            data = parse_data_format(raw_data,None)

        if data:
            response_data['data'] = data
        response_data['machine'] = machine
        res['response'].append(response_data)

    return jsonify(res),200  


@app.route('/apis/dtac/getContactLogs/<string:find_text>', methods=['GET'])
def get_contact_dtac(find_text):

    res = {
        "response":[]
    }

    start_date = request.args.get('date')
    status = request.args.get('status')
    detail = request.args.get('find')

    cmd = f"cd {log_path.LOG_CONTACT_PATH} ; grep {find_text} *.csv"
    for machine,server in log_path.DTAC_SERVER.items():
        response_data = {
            "machine":'',
            "data": None
        }
        raw_data = SSHConnect.ssh_connect(host=server.get('host'), username=server.get('user'),password=server.get('password'), port=server.get('port'),command=cmd)
        
        data = None
        if start_date:
            data = parse_data_format(raw_data,start_date)
        else:
            data = parse_data_format(raw_data,None)

        if data:
            response_data['data'] = data
        response_data['machine'] = machine
        res['response'].append(response_data)

    return jsonify(res),200  




@app.route('/apis/true/getResponseLogs/<string:find_text>', methods=['GET'])
def get_response_true(find_text):

    res = {
        "response":[]
    }

    start_date = request.args.get('date')
    status = request.args.get('status')
    detail = request.args.get('find')

    cmd = f"cd {log_path.LOG_RESPONSE_PATH} ; grep {find_text} *.csv"
    for machine,server in log_path.TRUE_SERVER.items():
        response_data = {
            "machine":'',
            "data": None
        }
        raw_data = SSHConnect.ssh_connect(host=server.get('host'), username=server.get('user'),password=server.get('password'), port=server.get('port'),command=cmd)
        
        data = None
        if start_date:
            data = parse_data_format(raw_data,start_date)
        else:
            data = parse_data_format(raw_data,None)

        if data:
            response_data['data'] = data
        response_data['machine'] = machine
        res['response'].append(response_data)

    return jsonify(res),200


@app.route('/apis/true/getContactLogs/<string:find_text>', methods=['GET'])
def get_contact_true(find_text):

    res = {
        "response":[]
    }

    start_date = request.args.get('date')
    status = request.args.get('status')
    detail = request.args.get('find')

    cmd = f"cd {log_path.LOG_CONTACT_PATH} ; grep {find_text} *.csv"
    for machine,server in log_path.TRUE_SERVER.items():
        response_data = {
            "machine":'',
            "data": None
        }
        raw_data = SSHConnect.ssh_connect(host=server.get('host'), username=server.get('user'),password=server.get('password'), port=server.get('port'),command=cmd)
        
        data = None
        if start_date:
            data = parse_data_format(raw_data,start_date)
        else:
            data = parse_data_format(raw_data,None)

        if data:
            response_data['data'] = data
        response_data['machine'] = machine
        res['response'].append(response_data)

    return jsonify(res),200  


def parse_data_format(raw_data,since_date):
    data = str(raw_data).split('\n')

    if not since_date:
        return data
    else:
        date_formate = change_date_format(since_date)
        res = []
        if data:
            for read_data in data:
                if date_formate in read_data:
                    res.append(read_data)

    return res


def change_date_format(date_str):
    try:
        # Convert string to datetime object
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # Convert datetime object to new string format
        new_date_str = date_obj.strftime('%m/%d/%Y')
    except:
        print("Error while parse format date")    
    return new_date_str


if __name__ == '__main__':
    # app.run(host="0.0.0.0",debug=True)
    app.run()