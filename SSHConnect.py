import paramiko
import log_path
import re

def ssh_connect(host, username, password, port=22,command='ls'):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, timeout=10)
        [stdin,file,stderr] = ssh.exec_command(command=command,timeout=10)
        res = file.read().decode('utf-8').strip()
        ssh.close()
    except Exception as e:
        error_message = f"Error: {e} , {stderr.read().decode('utf-8').strip()}"
        print(error_message)  # Keep the print for debugging
        return error_message, 500  # Return the error message and a 500 status code
    return res



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
            # print(read_data)
            res['response']['data'].append(read_data)
    # print(res)
    return res



# find_text = "TRUEAPP"

# cmd = f"cd {log_path.LOG_RESPONSE_PATH} ; grep {find_text} *.csv"

# for machine,server in log_path.DTAC_SERVER.items():
#     # print(machine,server)
#     raw_data = ssh_connect(host=server.get('host'), username=server.get('user') ,password=server.get('password'),port=server.get('port'),command=cmd)
#     # raw_data = SSHConnect.ssh_connect('192.168.1.135',log_path.user_name,log_path.password,command=cmd) # ip, username, password, port, command
#     # print(raw_data)
#     # res = parse_data_format(raw_data,None)
# # raw_data = ssh_connect('localhost',username='danateq',password='DTN@danateq202106',command=cmd)
# # print(raw_data)