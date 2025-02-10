import paramiko
import log_path
import re

def ssh_connect(ip, username, password, port=22,command='ls'):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password, timeout=10)
        [stdin,file,stderr] = ssh.exec_command(command=command,timeout=10)
        res = file.read().decode('utf-8').strip()
        ssh.close()
    except Exception as e:
        error_message = f"Error: {e}"
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
            print(read_data)
            res['response']['data'].append(read_data)
    print(res)
    return res



find_text = '678'
cmd = f"cd {log_path.LOG_CONTACT_PATH} ; grep {find_text} *.csv"
res = ssh_connect('192.168.1.135','danateq','DTN@danateq202401',command=cmd) # ip, username, password, port, command
parse_data_format(res,None)