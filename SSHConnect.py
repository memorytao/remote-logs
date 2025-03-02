import paramiko
import log_path

def ssh_connect(host, username, password, port=22,command='ls'):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, timeout=10)
        [stdin,file,stderr] = ssh.exec_command(command=command,timeout=10)
        res = file.read().decode('utf-8').strip()
    except Exception as e:
        error_message = f"Error: {e} , {stderr.read().decode('utf-8').strip()}"
        print(error_message)  # Keep the print for debugging
        return error_message, 500  # Return the error message and a 500 status code
    finally:
        ssh.close()
    return res


if __name__ == '__main__':
    DTAC = log_path.DTAC_SERVER
    cmd = "cd /opt/link/log/trans_log/response_history ; grep 66805155184 *.csv"
    ssh_connect(DTAC['AGW01']['host'], DTAC['AGW01']['user'], DTAC['AGW01']['password'], DTAC['AGW01']['port'], cmd)