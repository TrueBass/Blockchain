import sys
import socket, multiprocessing


def job(connection, address, config):
  while True:
    message = connection.recv(1024)
    message = message.decode()

    print(f"Message from client ip={address[0]}, port={address[1]}:", message)

    if message == "exit" or len(message) == 0:
      break

    forward_message(config, message)
    config["forwarded"].append(address[0])

  connection.close()
  print(f"End connection with ip={address[0]}, port={address[1]}")


def forward_message(config, message):
  for h in config["hosts"]:
    if h["forwarded"] > 1:
      h["forwarded"] = 0
      break
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
    port = sys.argv[1]

  config["port"] = int(port)



if __name__ == "__main__":
  config = {"forwarded": []}
  
  get_command_line_argument(config)
  get_config_from_file(config)
  server(config)