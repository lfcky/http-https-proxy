import socket
import threading
import select
import time
import traceback

SERVER_HOST = '139.129.231.224'
SERVER_PORT = 2080
LOCAL_PORT = 2080
# ali 139.129.231.224  vultr 149.28.56.175

key = '2'
keys = []
length = len(key)
for k in key:
    keys.append(ord(k))


def code(bytes):
    index = 0
    result = b''
    for b in bytes:
        result += (b ^ keys[index]).to_bytes(1, 'big')
        index += 1
        index %= length
    return result


def tcpConnection(client, addr):
    server = host = ''
    try:
        data = client.recv(4096)
        header = {}
        heads = data.decode().split('\r\n')[1:]
        for head in heads:
            hs = head.split(': ')
            if len(hs) < 2:
                continue
            header[hs[0]] = hs[1:]
        host = header['Host'][0]
        port = host.split(':')
        if len(port) > 1:
            host = port[0]
            port = int(port[1])
        else:
            port = 80
        host = str(host)
        log(host, '建立连接')
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((SERVER_HOST, SERVER_PORT))
        server.sendall(code(('lf;' + host + ';' + str(port)).encode()))
        checkData = server.recv(4096)
        if checkData.decode() != 'ok':
            log(host, '验证错误')
            server.close()
            client.close()
            return
        log(host, '验证通过')
        # 处理https
        if port != 80:
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            client.sendall(("HTTP/1.1 200 Connection Established\r\nFiddlerGateway: Direct\r\nStartTime: " + start_time + "\r\nConnection: close\r\n\r\n").encode())
        else:
            log(host, 'http请求头')
            server.sendall(code(data))
        inputs = [client, server]
        outputs = []
        while True:
            readable, writable, _ = select.select(inputs, outputs, inputs)
            for readSocket in readable:
                data = readSocket.recv(4096)
                if data == b'':
                    log(host, '断开连接')
                    client.close()
                    server.close()
                    return
                if readSocket is client:
                    log(host, '发送数据')
                    server.sendall(code(data))
                else:
                    log(host, '接收数据')
                    client.sendall(code(data))
    except Exception as e:
        if server != '':
            server.close()
        client.close()
        traceback.print_exc()
        log(host, 'error')

hosts = []
def log(host, msg):
    if len(hosts) == 0:
        print(host + ' ' + msg)
        return
    for h in hosts:
        if h in host:
            print(host + ' ' + msg)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', LOCAL_PORT))
s.listen(1024)
while True:
    client, addr = s.accept()
    thread = threading.Thread(target=tcpConnection, args=(client, addr))
    thread.start()
