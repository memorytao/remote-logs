from flask import Flask, request, jsonify
from pathlib import Path
import SSHConnect
import log_path
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "API's working!"

# @app.route('/items', methods=['GET'])
# def get_items():
#     return jsonify(items)

# @app.route('/items/<int:item_id>', methods=['GET'])
# def get_item(item_id):
#     item = next((item for item in items if item['id'] == item_id), None)
#     if item:
#         return jsonify(item)
#     else:
#         return jsonify({'message': 'Item not found'}), 404

# @app.route('/items', methods=['POST'])
# def create_item():
#     new_item = request.get_json()
#     new_item['id'] = len(items) + 1
#     items.append(new_item)
#     return jsonify(new_item), 201

# @app.route('/items/<int:item_id>', methods=['PUT'])
# def update_item(item_id):
#     item = next((item for item in items if item['id'] == item_id), None)
#     if item:
#         data = request.get_json()
#         item.update(data)
#         return jsonify(item)
#     else:
#         return jsonify({'message': 'Item not found'}), 404

# @app.route('/items/<int:item_id>', methods=['DELETE'])
# def delete_item(item_id):
#     global items
#     items = [item for item in items if item['id'] != item_id]
#     return jsonify({'message': 'Item deleted'})


@app.route('/apis/dtac/getResponseLog/demo/<string:find_text>', methods=['GET'])
def get_all_reponse_dtac(find_text):

    res = {
        "response":[]
    }

    start_date = request.args.get('startDate')
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


@app.route('/apis/dtac/getContactLog/demo/<string:find_text>', methods=['GET'])
def get_all_contact_dtac(find_text):

    res = {
        "response":[]
    }

    start_date = request.args.get('startDate')
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


@app.route('/apis/dtac/getResponseLog/demo', methods=['POST'])
def get_resonse_by():
    req = request.get_json()
    find_text = req['wordsTofind']
    date_find = req['sinceDate']
    cmd = f"cd {log_path.LOG_RESPONSE_PATH} ; grep {find_text} *.csv"
    res = {
        "response":[]
    }
    for machine,server in log_path.DTAC_SERVER.items():
        response_data = {
            "machine":'',
            "data": []
        }
        raw_data = SSHConnect.ssh_connect(host=server.get('host'), username=server.get('user'),password=server.get('password'), port=server.get('port'),command=cmd)
        
        if date_find:
            found_data = parse_data_format(raw_data,date_find)
            response_data['machine'] = machine
            response_data['data'] = found_data
            res['response'].append(response_data)
        else:
            response_data['machine'] = machine
            response_data['data'] = found_data
            res['response'].append(response_data)

    return jsonify(res),200  

@app.route('/apis/dtac/getResponseLog/<string:find_text>', methods=['GET'])
def get_response_dtac_log(find_text):
    res = get_data('./logs/dtac_response',find_text,None)
    return jsonify(res),200

@app.route('/apis/dtac/getContactLog/<string:find_text>', methods=['GET'])
def get_contact_dtac_log(find_text):
    res = get_data('./logs/dtac_contact',find_text,None)
    return jsonify(res),200

@app.route('/apis/dtac/getResponseLog', methods=['POST'])
def get_response_dtac_log_criteria():
    res = get_data('./logs/dtac_response',None,req= request.get_json())
    return jsonify(res),200

@app.route('/apis/true/getContactLog/<string:find_text>', methods=['GET'])
def get_contact_true_log(find_text):
    res = get_data('./logs/true_contact',find_text,None)
    return jsonify(res),200

@app.route('/apis/true/getResponse/<string:find_text>', methods=['GET'])
def get_response_true_log(find_text):
    res = get_data('./logs/true_contact',find_text,None)
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



def get_data(log_path,find_text,req):
    folder_path =  Path(log_path)
    res = {'response': []}
    data_found = []
    for files in folder_path.glob('*.csv'):
        with files.open('r',encoding='utf-8') as f:
            if data_found:
                new_data = {
                    'data': data_found,
                    'fileName': files.name,
                }
                res['response'].append(new_data)
                data_found = []
            for data_log in f:
                if req:
                    date_from = req['dateFrom']
                    date_to = req['dateTo']
                    msisdn = req['msisdn']
                    if date_from in data_log and date_to in data_log and msisdn in data_log:
                        data_found.append(data_log.replace('\n',''))
                elif find_text in data_log:
                    data_found.append(data_log.replace('\n',''))
    return res


def change_date_format(date_str):
    # Convert string to datetime object
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    # Convert datetime object to new string format
    new_date_str = date_obj.strftime('%m/%d/%Y')
    
    return new_date_str


if __name__ == '__main__':
    # app.run(host="0.0.0.0",debug=True)
    app.run()