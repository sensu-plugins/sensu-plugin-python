import socket
import json


def push_event(sensu_client_host='127.0.0.1',
               sensu_client_port=3030,
               source=None,
               check_name=None,
               exit_code=None,
               message=None,
               **extra_vars):

    for param in [source, check_name, exit_code, message]:
        if param is None:
            raise ValueError
    message = {
        "source":  source,
        "name":    check_name,
        "status":  exit_code,
        "output":  message,
        }
    for key in extra_vars:
        message[key] = extra_vars[key]
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        sock.close()
        raise
    sock.connect((sensu_client_host, sensu_client_port))
    sock.send(json.dumps(message))
    if sock.recv(24) != "ok":
        sock.close()
        raise socket.error
