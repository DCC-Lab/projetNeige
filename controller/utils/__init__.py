import os
import paramiko


def readData(ser, N):
    data = []
    while len(data) != N:
        line = ser.readline()
        line = line[0:len(line)-2].decode("utf-8", errors='replace')
        try:
            vector = [float(e) for e in line.split(',')]
            if len(vector) == 4:
                data.append(vector)
        except ValueError:
            continue
    return data


def copyToServer(filepath, server="24.201.18.112", username="Alegria"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.connect(server, username=username)
    sftp = ssh.open_sftp()
    sftp.put(os.path.join(os.getcwd(), filepath), os.path.join("C:/SnowOptics", filepath))
    sftp.close()
    ssh.close()
