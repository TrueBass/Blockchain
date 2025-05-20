import socket, multiprocessing


def job(connection, address):
  while True:
    message = connection.recv(1024)
    message = message.decode()

    print(f"Message from client ip={address[0]}, port={address[1]}:", message)

    if message == "exit":
      break
    elif len(message) == 0:
      break

  connection.close()
  print(f"End connection with ip={address[0]}, port={address[1]}")

def server():
  host = socket.gethostname()
  ip = socket.gethostbyname(host)
  port = 5000

  server_socket = socket.socket()
  server_socket.bind((host, port))
  server_socket.listen(10)

  print(f"Start server: port={port}, host{host}, ip={ip}")

  while True:
    connection, address = server_socket.accept()
    print(f"Received connection from ip={address[0]}, port={address[1]}")
    worker = multiprocessing.Process(target=job, args=(connection, address))
    worker.start()

if __name__ == "__main__":
  server()