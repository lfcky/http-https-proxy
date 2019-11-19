import socket
import select
import threading

SERVER_HOST = '149.28.56.175'
SERVER_PORT = 2080
# ali 139.129.231.224  vultr 149.28.56.175
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
    host = server = ''
    try:
        data = client.recv(4096)
        password, host, port = code(data).decode().split(';')
        if password != 'lf':
            client.close()
            return
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((SERVER_HOST, SERVER_PORT))
        server.sendall(data)
        print(str(host) + ' relay')
        inputs = [client, server]
        while True:
            readable, _, __ = select.select(inputs, [], inputs)
            for r in readable:
                data = r.recv(4096)
                if data == b'':
                    server.close()
                    client.close()
                    print(host + ' end')
                    return
                if r is client:
                    print(host + ' forward to server')
                    server.sendall(data)
                else:
                    print(host + ' forward to client')
                    client.sendall(data)
    except Exception as e:
        client.close()
        if server != '':
            server.close()
        print(host + ' ' + str(e))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 2080))
s.listen(1024)
while True:
    client, addr = s.accept()
    thread = threading.Thread(target=tcpConnection, args=(client, addr))
    thread.start()
