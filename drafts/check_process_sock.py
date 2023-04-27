#!/usr/bin/env python
import os
import psutil
import subprocess

#res = subprocess.run(["ss2", "-x"], stdout=subprocess.PIPE)
#print(res)
pid = 1
#pid = 59745
sk_path = "/run/libvirt/libvirt-sock"
def check_ss():
    import shlex
    for conn in psutil.Process(pid).connections("unix"):
        socket = os.readlink(f"/proc/{pid}/fd/{conn.fd}")
        sk_inode = socket.split(':')[1].strip('[]')
        res = subprocess.run(shlex.split(f"ss -oH state connected '( dport = :{sk_inode} )' src = unix:{sk_path}"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        if res.stdout:
            print(f"Found matching connection {res.stdout} for {conn}")
            return True
    return False

def check_ss2():
    import json
    res = subprocess.run(["ss2", "-x"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    json_res = json.loads(res.stdout)["UNIX"]["flows"]
    for conn in psutil.Process(pid).connections("unix"):
        socket = os.readlink(f"/proc/{pid}/fd/{conn.fd}")
        sk_inode = int(socket.split(':')[1].strip('[]'))
        for s_conn in json_res:
            if s_conn.get("path_name") == sk_path:
                if s_conn.get("peer_inode") == sk_inode:
                    print(f"Found matching connection {s_conn} for {conn}")
                    return True
    return False

print(check_ss())

print(check_ss2())

