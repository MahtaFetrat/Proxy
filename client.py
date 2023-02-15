import socket

IP = 'localhost'
XCLIENT_IP = 'localhost'
BUFFSIZE = 1024


class Client:
    def __init__(self):
        self.udp_socket = self.bind_udp()
        self.xclient_addr = self.get_xclient_init_message()
        self.messages = ["Sample Message 1.", "Sample Message 2.", "Sample Message 3."]

    def bind_udp(self):
        udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_socket.bind((IP, 0))
        udp_socket_name = udp_socket.getsockname()[1]
        print(f"Listening UDP on {IP}:{udp_socket_name}")
        return udp_socket

    def get_xclient_init_message(self):
        _, addr = self.udp_socket.recvfrom(BUFFSIZE)
        return addr

    def send_sample_packets(self):
        for m in self.messages:
            self.udp_socket.sendto(m.encode(), self.xclient_addr)
            print(f"Sent {m}.")

    def receive_responses(self):
        for _ in range(self.messages):
            payload, _ = self.udp_socket.recvfrom(BUFFSIZE)
            print(f"Received: '{payload}'")

    def start(self):
        self.send_sample_packets()
        self.receive_responses()


if __name__ == "__main__":
    Client().start()
