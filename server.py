import socket
import threading
import select
import traceback

LOCAL_PORT = 2080

KEY = '2'
KEYS = []
LENGTH = len(KEY)
for k in KEY:
  KEYS.append(ord(k))

def code(bytes):
  index = 0
  result = b''
  for b in bytes:
    result += (b ^ KEYS[index]).to_bytes(1, 'big')
    index += 1
    index %= LENGTH
  return result

def tcpConnection(client, addr):
  host = server =  ''
  try:
    data = client.recv(4096)
    password, host, port = code(data).decode().split(';')
    if password != 'lf':
      client.sendall('refuse'.encode())
      client.close()
      return
    client.sendall('ok'.encode())
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((host, int(port)))
    print(str(host) + ' connected')
    inputs = [client, server]
    outputs = []
    while True:
      readable, _, __ = select.select(inputs, outputs, inputs)
      for read in readable:
        data = read.recv(4096)
        if read is client:
          if data == b'':
            print(host + ' client close')
            server.close()
            return
          print(host + ' send to server')
          server.sendall(code(data))
        else:
          if data == b'':
            print(host + ' server close')
            client.close()
            return
          print(host + ' send to client')
          client.sendall(code(data))
  except Exception as e:
    if server != '':
      server.close()
    client.close()
    traceback.print_exc()
    print(host + ' error ' + str(e))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', LOCAL_PORT))
s.listen(1024)
while True:
  client, addr = s.accept()
  thread = threading.Thread(target=tcpConnection, args=(client, addr))
  thread.start()

