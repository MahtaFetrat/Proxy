import socket
from utils import parse_message

IP = 'localhost'
BUFFSIZE = 1024

class Server:
    def __init__(self):
        self.udp_socket = None

    def bind_udp(self):
        self.udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_socket.bind((IP, 0))
        udp_socket_name = self.udp_socket.getsockname()[1]
        print(f"Listening UDP on {IP}:{udp_socket_name}")

    @staticmethod
    def build_response(message):
        return message.capitalize() * 2

    def handle_requests(self):
        while True:
            message, addr = self.udp_socket.recvfrom(BUFFSIZE) 
            _, payload = parse_message(message)
            response = self.build_response(payload)
            self.udp_socket.sendto(response.encode(), addr)

    def start(self):
        self.bind_udp()
        self.handle_requests()

if __name__ == "__main__":
    Server().start()
