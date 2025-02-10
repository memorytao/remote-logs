from flask import Flask, request, jsonify
from pathlib import Path
import SSHConnect
import log_path

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


@app.route('/apis/dtac/demo/<string:find_text>', methods=['GET'])
def get_contact_dtac_log_all(find_text):
    cmd = f"cd {log_path.LOG_RESPONSE_PATH} ; grep {find_text} *.csv"
    raw_data = SSHConnect.ssh_connect('192.168.1.135',log_path.user_name,log_path.password,command=cmd) # ip, username, password, port, command
    res = parse_data_format(raw_data,None)
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

def parse_data_format(find_text, req):
    res = {
        "response": {
            "machine": "DTAC_AGW01",
            "data": []
        }
    }
    raw_data = str(find_text).split('\n')
    if raw_data:
        for read_data in raw_data:
            res['response']['data'].append(read_data)
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



if __name__ == '__main__':
    # app.run(host="0.0.0.0",debug=True)
    app.run()