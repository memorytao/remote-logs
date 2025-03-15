from flask import Flask, request, jsonify
import logging
import SSHConnect
import log_path
from flask_cors import CORS

TRUE_SITE = "TRUE"
DTAC_SITE = "DTAC"

app = Flask(__name__)
# Configure logging
logging.basicConfig(filename="api.log", level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "API's working!"

def get_logs(server_dict, log_path, find_text, body):

    sort = body.get('sort')
    mainSearch = body.get('mainSearch')
    optionalSearch = body.get('optionalSearch')
    status = body.get('status')

    res = {"response": []}
    sortBy = 'sort -k1,1' if sort == 'oldest' else 'sort -k1,1r'
    cmd = f"cd {log_path} ; grep '{find_text}' *.csv | {sortBy} | head -n 1000 ;"
    app.logger.info(f"execute command: {cmd}")
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
                 if ((not mainSearch or mainSearch in data) and
                    (not optionalSearch or optionalSearch in data) and
                    (not status or status in data)):
                    response_data['data'].append(data)
        res['response'].append(response_data)
        response_data['machine'] = machine
    return res

def get_what_to_find(obj):
    
    if obj.get('mainSearch'):
        return obj.get('mainSearch')
    elif obj.get('optionalSearch'):
        return obj.get('optionalSearch')
    elif obj.get('status'):
        return obj.get('status')
    elif obj.get('sort'):
        return obj.get('sort')
    return

@app.route('/apis/dtac/getResponseLog', methods=['POST'])
def getResponseLogDTAC():
    body = request.get_json()
    get_req_log(DTAC_SITE,body=body)
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.DTAC_SERVER, log_path.LOG_RESPONSE_PATH,first_to_find,body)
    return jsonify(res), 200

@app.route('/apis/dtac/getContactLog', methods=['POST'])
def getContactLogDTAC():
    body = request.get_json()
    get_req_log(DTAC_SITE,body=body)
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.DTAC_SERVER, log_path.LOG_CONTACT_PATH,first_to_find, body)
    return jsonify(res), 200


@app.route('/apis/true/getResponseLog', methods=['POST'])
def getResponseLogTRUE():
    body = request.get_json()
    get_req_log(TRUE_SITE,body=body)
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.TRUE_SERVER, log_path.LOG_RESPONSE_PATH, first_to_find, body)
    return jsonify(res), 200

@app.route('/apis/true/getContactLog', methods=['POST'])
def getContactLogTRUE():
    body = request.get_json()
    get_req_log(TRUE_SITE,body=body)
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.TRUE_SERVER, log_path.LOG_CONTACT_PATH, first_to_find, body)
    return jsonify(res), 200

def get_req_log(brand,body):
    app.logger.info(f"Incoming request | Brand: {brand}, Body: {body}")


if __name__ == '__main__':
    app.run()