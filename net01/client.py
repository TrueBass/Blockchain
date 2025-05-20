import socket

def client():
  host = socket.gethostname()
  ip = socket.gethostbyname(host)
  port_server = 5000

  client_socket = socket.socket()
  client_socket.connect((host, port_server))
  client_own_address = client_socket.getsockname()

  print(f"Start client: port={client_own_address[1]}, connect with host{host}, ip={ip}")

  while True:
    message = input("% ")
    
    client_socket.send(message.encode())
    if message == "exit": break
  
  client_socket.close()

if __name__ == "__main__":
  client()