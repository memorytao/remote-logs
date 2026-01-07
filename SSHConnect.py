import paramiko


def ssh_connect(host, username, password, port=22, command="pwd", machine=None):
    ssh = None
    stderr = None
    res = {}
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"Connecting to {machine} : {host}...")  # Debug 1
        ssh.connect(host, port, username, password, timeout=30)

        print(f"Executing: {command}")  # Debug 2
        stdin, stdout, stderr = ssh.exec_command(command=command, timeout=30)
        data = stdout.read().decode("utf-8").strip()

        err_data = stderr.read().decode("utf-8").strip()
        if err_data:
            print(f"Command STDERR: {err_data}")

        res[machine] = data

    except Exception as e:
        stderr_output = ""
        if "stderr" in locals() and stderr is not None:
            try:
                stderr_output = stderr.read().decode("utf-8").strip()
            except Exception:
                pass

        print(f"CRITICAL ERROR: {e}")
        print(f"STDERR BUFFER: {stderr_output}")

        error_message = f"Error: {str(e)} , {stderr_output}"
        return error_message, 500
    finally:
        if ssh is not None:
            ssh.close()
    return res


if __name__ == "__main__":
    TARGET_HOST = "192.168.26.149"
    cmd = "cd /opt/link/log/trans_log/response_history ; grep -E '66634718198_20250226113438981' * | sed -n '1,10p'"
    res = ssh_connect(
        host=TARGET_HOST,
        username="danateq",
        password="DTN@danateq202106",
        port=22,
        command=cmd,
        machine="AGW01",
    )
    print("Result:", res)
