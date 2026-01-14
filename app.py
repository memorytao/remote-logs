from flask import Flask, request, jsonify
import SSHConnect
import log_path
import re
from flask_cors import CORS

TRUE_SITE = "TRUE"
DTAC_SITE = "DTAC"
TOL_SITE = "TOL"

app = Flask(__name__)

CORS(app)


@app.route("/", methods=["GET"])
def home():
    return "API's working!"


def escape_special_chars(param):
    return re.sub(r"[;\.\(\)\*]", r"\\\g<0>", param)


def make_command(items):

    cmd = ""
    for item in items:
        try:
            if item == "":
                continue
            if cmd == "":
                cmd = f" grep -E '{item}' *.csv"
            else:
                cmd += f" | grep -E '{item}'"
        except Exception as e:
            print(f"Error creating command: {e}")
    return cmd


def build_grep_pipeline(query):
    """
    To convert string param
    """
    query = query.strip()
    if not query:
        return ""

    stages = [s.strip() for s in query.split(",") if s.strip()]

    cmds = []
    for i, stage in enumerate(stages):
        parts = [p.strip() for p in stage.split(";") if p.strip()]
        if not parts:
            continue

        if len(parts) > 1:
            # for OR operation
            pattern = "|".join(parts)
            base = "grep -E"
        else:
            # for AND operation 
            pattern = parts[0]
            base = "grep"

        if i == 0:
            cmd = f"{base} '{pattern}' *.csv"
        else:
            cmd = f"{base} '{pattern}'"

        cmds.append(cmd)

    return " | ".join(cmds)


@app.route("/api/v1/getlog", methods=["POST"])
def get_logs_server():

    servers = {}
    res = {}
    body = request.get_json()
    brand = body.get("brand")
    log = body.get("log")
    params = body.get("value")
    start = body.get("start", 1)
    end = body.get("end", 500)
    end = 600

    print(
        f"Received parameters: brand={brand}, log={log}, value={params}, start={start}, end={end}"
    )

    items = []
    if params.find(",") != -1:
        items = [item.strip() for item in params.split(",")]

    elif params.find(";") != -1:
        prepare = [item.strip() for item in params.split(";")]
        items.append("|".join(prepare))
    else:
        items.append(params.strip())

    if brand not in [TRUE_SITE, DTAC_SITE, TOL_SITE]:
        return jsonify("Error: Invalid brand. Must be 'TRUE' or 'DTAC' or 'TOL'."), 400
    if log not in ["response", "contact"]:
        return jsonify("Error: Invalid log type. Must be 'response' or 'contact'."), 400
    if not items:
        return jsonify("Error: 'value' parameter is required and cannot be empty."), 400

    if brand == TRUE_SITE:
        servers = log_path.TRUE_SERVER
    elif brand == DTAC_SITE:
        servers = log_path.DTAC_SERVER
    elif brand == TOL_SITE:
        servers = log_path.TOL_SERVER

    res = {}
    res_logs = []
    for machine, server in servers.items():
        dir_log = None

        if brand != TOL_SITE:
            dir_log = (
                log_path.LOG_RESPONSE_PATH
                if log == "response"
                else log_path.LOG_CONTACT_PATH
            )
        else:
            dir_log = (
                log_path.TOL_RESPONSE_PATH
                if log == "response"
                else log_path.TOL_LOG_CONTACT_PATH
            )
        cmd = build_grep_pipeline(params)
        # print(f"CMDs {cmds}")
        # cmd = make_command(items)
        cmd = f"cd {dir_log} ; {cmd} | sed -n '{start},{end}p' | sort -r ;"
        res_logs.append(get_logs_data(cmd, **server, machine=machine))

    res["response"] = res_logs
    count_response = 0
    for machine_data in res["response"]:
        for machine, data in machine_data.items():
            if data == "":
                count_response += 1

    if count_response == len(res["response"]):
        res["response"] = []
        return jsonify(res), 200

    return jsonify(res), 200


def get_logs_data(cmd, **kwargs):

    app.logger.info(f"Executing command: {cmd} on machine: {kwargs.get('machine')}")
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
    # app.logger.info(f"Received data: {res} from machine: {kwargs.get('machine')}")
    return res


if __name__ == "__main__":
    # app.run(debug=True, port=8889)
    app.run()
