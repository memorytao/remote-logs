from flask import Flask, request, jsonify
import logging
import SSHConnect
import log_path
from flask_cors import CORS

TRUE_SITE = "TRUE"
DTAC_SITE = "DTAC"

app = Flask(__name__)
# Configure logging
logging.basicConfig(
    filename="api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return "API's working!"


def get_logs(server_dict, log_path, find_text, body):

    sort = body.get("sort")
    mainSearch = body.get("mainSearch")
    optionalSearch = body.get("optionalSearch")
    status = body.get("status")

    res = {"response": []}
    sortBy = "sort -k1,1" if sort == "oldest" else "sort -k1,1r"
    cmd = f"cd {log_path} ; grep '{find_text}' *.csv | {sortBy} | head -n 1000 ;"
    app.logger.info(f"execute command: {cmd}")
    for machine, server in server_dict.items():
        response_data = {"machine": "", "data": []}
        raw_data = SSHConnect.ssh_connect(
            host=server.get("host"),
            username=server.get("user"),
            password=server.get("password"),
            port=server.get("port"),
            command=cmd,
        )
        # If ssh_connect returns (output, status), get output
        output = raw_data[0] if isinstance(raw_data, tuple) else raw_data
        for data in str(output).split("\n"):
            if data:
                if (
                    (not mainSearch or mainSearch in data)
                    and (not optionalSearch or optionalSearch in data)
                    and (not status or status in data)
                ):
                    response_data["data"].append(data)
        res["response"].append(response_data)
        response_data["machine"] = machine
    return res


def get_what_to_find(obj):

    if obj.get("mainSearch"):
        return obj.get("mainSearch")
    elif obj.get("optionalSearch"):
        return obj.get("optionalSearch")
    elif obj.get("status"):
        return obj.get("status")
    elif obj.get("sort"):
        return obj.get("sort")
    return


@app.route("/apis/dtac/getResponseLog", methods=["POST"])
def getResponseLogDTAC():
    body = request.get_json()
    get_req_log(DTAC_SITE, body=body)
    first_to_find = get_what_to_find(body)
    res = get_logs(
        log_path.DTAC_SERVER, log_path.LOG_RESPONSE_PATH, first_to_find, body
    )
    return jsonify(res), 200


@app.route("/apis/dtac/getContactLog", methods=["POST"])
def getContactLogDTAC():
    body = request.get_json()
    get_req_log(DTAC_SITE, body=body)
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.DTAC_SERVER, log_path.LOG_CONTACT_PATH, first_to_find, body)
    return jsonify(res), 200


@app.route("/apis/true/getResponseLog", methods=["POST"])
def getResponseLogTRUE():
    body = request.get_json()
    get_req_log(TRUE_SITE, body=body)
    first_to_find = get_what_to_find(body)
    res = get_logs(
        log_path.TRUE_SERVER, log_path.LOG_RESPONSE_PATH, first_to_find, body
    )
    return jsonify(res), 200


@app.route("/apis/true/getContactLog", methods=["POST"])
def getContactLogTRUE():
    body = request.get_json()
    get_req_log(TRUE_SITE, body=body)
    first_to_find = get_what_to_find(body)
    res = get_logs(log_path.TRUE_SERVER, log_path.LOG_CONTACT_PATH, first_to_find, body)
    return jsonify(res), 200


def get_req_log(brand, body):
    app.logger.info(f"Incoming request | Brand: {brand}, Body: {body}")


def make_command(items):

    cmd = ""
    for item in items:
        try:
            if cmd == "":
                cmd = f" grep -E '{item.strip()}' *.csv"
            else:
                cmd += f" | grep -E '{item.strip()}'"
        except Exception as e:
            print(f"Error creating command: {e}")
            logging.error(f"Error creating command: {e}")
    return cmd


@app.route("/api/v1/getlog", methods=["POST"])
def get_logs_server():

    servers = {}
    res = {}
    body = request.get_json()
    brand = body.get("brand")
    log = body.get("log")
    params = body.get("value")
    start = body.get("start", 1)
    end = body.get("end", 40)

    # print("Received parameters:", brand, log, params, start, end)
    logging.info(f"Received parameters: {brand}, {log}, {params}, {start}, {end}")

    items = []
    if params.find(";") != -1:
        items.append(params.replace(";", "|"))
    elif params.find(",") != -1:
        items = params.split(",")
    else:
        items.append(params)

    if brand not in [TRUE_SITE, DTAC_SITE]:
        return jsonify("Error: Invalid brand. Must be 'TRUE' or 'DTAC'."), 400
    if log not in ["response", "contact"]:
        return jsonify("Error: Invalid log type. Must be 'response' or 'contact'."), 400
    if not items:
        return jsonify("Error: 'value' parameter is required and cannot be empty."), 400

    if brand == TRUE_SITE:
        servers = log_path.TRUE_SERVER
    elif brand == DTAC_SITE:
        servers = log_path.DTAC_SERVER

    res = {}
    res_logs = []
    for machine, server in servers.items():
        dir_log = (
            log_path.LOG_RESPONSE_PATH
            if log == "response"
            else log_path.LOG_CONTACT_PATH
        )
        cmd = make_command(items)
        cmd = f"cd {dir_log} ; {cmd} | sed -n '{start},{end}p' ;"
        res_logs.append(get_logs_data(cmd, **server, machine=machine))
    res["response"] = res_logs

    for machine_data in res["response"]:
        count = 0
        for machine, data in machine_data.items():
            if data == "":
                count += 1
        if count == len(machine_data):
            res["response"] = []
            return jsonify(res), 200

    return jsonify(res), 200


def get_logs_data(cmd, **kwargs):

    res = SSHConnect.ssh_connect(
        host=kwargs.get("host"),
        username=kwargs.get("user"),
        password=kwargs.get("password"),
        port=22,
        command=cmd,
        machine=kwargs.get("machine"),
    )

    if isinstance(res, bytes):
        res = res.decode("utf-8")
    return res


if __name__ == "__main__":
    app.run(debug=True, port=8888)
    # app.run()
