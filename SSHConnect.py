import paramiko

def ssh_connect(host, username, password, port=22,command='pwd',machine=None):
    ssh = None
    stderr = None
    res = {}
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username, password, timeout=10)

        [stdin,stdout,stderr] = ssh.exec_command(command=command,timeout=10)
        data = stdout.read().decode('utf-8').strip()
        res[machine] = data

    except Exception as e:
        stderr_output = ""
        if stderr is not None:
            try:
                stderr_output = stderr.read().decode('utf-8').strip()
            except Exception:
                stderr_output = ""
        error_message = f"Error: {e} , {stderr_output}"
        # print(error_message)  # Keep the print for debugging
        return error_message, 500  # Return the error message and a 500 status code
    finally:
        if ssh is not None:
            ssh.close()
    return res
