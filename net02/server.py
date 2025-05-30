from typing import Any

import sys
import socket, multiprocessing
import multiprocessing.managers


def job(connection, address, config):
  while True:
    message = connection.recv(1024)
    message = message.decode()
    
    if message == "exit" or len(message) == 0:
      break

    print(f"Message from client ip={address[0]}, port={address[1]}:", message)

    if forward_message(config, message):
      break

  connection.close()
  print(f"End connection with ip={address[0]}, port={address[1]}")


def forward_message(config, message):
  for h in config["hosts"]:
    if h["forwarded"] == 1:
      print("======\nAlready Forwarded. Breaking.\n======")
      h["forwarded"] = 0
      return True
    else:
      h["forwarded"] += 1

    host = h["ip"]
    port = 5000 if "port" not in h else h["port"]

    print(f"Forward message to host={host}, port={port}")

    client_socket = socket.socket()
    client_socket.connect((host, port))

    msg_len = len(message)
    total_sent = 0
    while total_sent < msg_len:
      sent = client_socket.send(message[total_sent:].encode())
      if sent == 0:
        print("==========\nBroken Froward\n==========")
        return
      total_sent += sent
      print(f"=> sent {total_sent}B of {msg_len}")

    client_socket.close()
  return False


def server(config):
  host = socket.gethostname()
  ip = socket.gethostbyname(host)
  port = config["port"]

  server_socket = socket.socket()
  server_socket.bind((host, port))
  server_socket.listen(10)

  print(f"{'='*50}\nStart server: port={port}, host={host}, ip={ip}\n{'='*50}")

  while True:
    connection, address = server_socket.accept()
    print(f"Received connection from ip={address[0]}, port={address[1]}")
    worker = multiprocessing.Process(target=job, args=(connection, address, config))
    worker.start()


def get_config_from_file(config):
  config["hosts"] = []

  with open("config.txt", "r") as config_file:
    lines = config_file.readlines()

    for line in lines:
      line = line.strip()
      data = line.split()
      config["hosts"].append({
        "ip": data[0],
        "port": 5000 if len(data) == 1 else int(data[1]),
        "forwarded": 0
      })


def get_command_line_argument(config):
  DEFAULT_SERVER_PORT = 5000
  port = None

  if len(sys.argv) == 1:
    port = DEFAULT_SERVER_PORT
  elif len(sys.argv) == 2:
    port = int(sys.argv[1])

  config["port"] = port


def make_shared_config(config: dict[str, Any], manager: multiprocessing.managers.SyncManager) -> multiprocessing.managers.DictProxy:
  """Converts config into a shared multiprocessing dict.\n
  Without that,child processes couldn't affect config globally.\n
  They change their copy of the config
  """
  shared_config = manager.dict()
  shared_hosts = manager.list()

  for host_data in config["hosts"]:
    shared_host_dict = manager.dict(host_data)
    shared_hosts.append(shared_host_dict)

  shared_config["hosts"] = shared_hosts
  shared_config["port"] = config["port"]
  return shared_config


if __name__ == "__main__":
  config = {}

  manager = multiprocessing.Manager()
  
  get_command_line_argument(config)
  get_config_from_file(config)
  shared_config = make_shared_config(config, manager)
  server(shared_config)
  manager.shutdown()