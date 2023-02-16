import socket

IP = 'localhost'
BUFF_SIZE = 1024


class Client:
    def __init__(self):
        self.udp_socket = None
        self.xclient_addr = None
        self.messages = ["Sample Message 1.", "Sample Message 2.", "Sample Message 3."]

    def bind_udp(self):
        self.udp_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.udp_socket.bind((IP, 0))
        udp_socket_name = self.udp_socket.getsockname()[1]
        print(f"Listening UDP on {IP}:{udp_socket_name}")

    def get_xclient_init_message(self):
        _, addr = self.udp_socket.recvfrom(BUFF_SIZE)
        self.xclient_addr = addr

    def send_sample_packets(self):
        for message in self.messages:
            self.udp_socket.sendto(message.encode(), self.xclient_addr)
            print(f"Sent message '{message}'.")

    def receive_responses(self):
        for _ in self.messages:
            message, _ = self.udp_socket.recvfrom(BUFF_SIZE)
            print(f"Received message '{message.decode()}'")

    def start(self):
        self.bind_udp()
        self.get_xclient_init_message()
        if input() == "start":
            self.send_sample_packets()
            self.receive_responses()


if __name__ == "__main__":
    Client().start()
