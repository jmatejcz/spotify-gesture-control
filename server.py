import socket


class Socket:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_name = socket.gethostname()
        self.ip = socket.gethostbyname(self.host_name)
        self.port = 80

    def send_detected_gesture(self, gesture_id):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.port))
        client_socket.send(bytes(str(gesture_id), "utf-8"))


def main():
    host_name = socket.gethostname()
    ip = socket.gethostbyname(host_name)
    print(ip)
    port = 80
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    client_string = ""
    server_socket.listen(5)

    while client_string != "-1":
        server_socket.listen(5)

        client, address = server_socket.accept()
        print(f"Connection ok - {address[0]}:{address[1]}")

        client_string = client.recv(4)
        client_string = client_string.decode("utf-8")
        print(client_string)

        client.close()


if __name__ == '__main__':
    main()
