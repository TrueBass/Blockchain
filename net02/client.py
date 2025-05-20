import sys
import socket

def client(config):
  host = socket.gethostname()
  ip = socket.gethostbyname(host)
  port_server = config["server_port"]

  client_socket = socket.socket()
  client_socket.connect((host, port_server))
  client_own_address = client_socket.getsockname()

  print(f"Start client: port={client_own_address[1]}, connect with host{host}, ip={ip}")

  while True:
    message = input(f"{host}/{ip}/% ")
    
    client_socket.send(message.encode())
    if message == "exit": break
  
  client_socket.close()

def get_command_line_argument(config):
  DEFAULT_SERVER_PORT = 5000
  port = None

  if len(sys.argv) == 1:
    port = DEFAULT_SERVER_PORT
  elif len(sys.argv) == 2:
    port = sys.argv[1]

  config["server_port"] = int(port)


if __name__ == "__main__":
  config = {}
  get_command_line_argument(config)
  client(config)