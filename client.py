# create a client app program

import socket
import time

# IP of the client app
IP = 'localhost'

# initiate the buffer size for reading and receiving from the sockets
BUFF_SIZE = 1024


# create a Client class representing the client app
class Client:
    def __init__(self):
        # consider a udp socket for the transmissions between client app and x-client
        self.udp_socket = None
        # the IP address and port of x-client
        self.xclient_addr = None
        # initialize some sample messages to send to server app
        self.messages = ["Sample Message 1.", "Sample Message 2.", "Sample Message 3."]

    def bind_udp(self):
        # create the udp socket for the transmissions between client app and x-client
        self.udp_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # bind the udp socket to a free port
        self.udp_socket.bind((IP, 57078))
        # get the port assigned to the udp socket and print it
        udp_socket_name = self.udp_socket.getsockname()[1]
        print(f"Listening UDP on {IP}:{udp_socket_name}")

    def get_xclient_init_message(self):
        # receive the first message(the address of the udp socket) from x-client through the udp socket
        _, addr = self.udp_socket.recvfrom(BUFF_SIZE)
        # set the value of x-client address
        self.xclient_addr = addr

    def send_sample_packets(self):
        for message in self.messages:
            # endode and send the sample messages to x-client through udp socket
            self.udp_socket.sendto(message.encode(), self.xclient_addr)
            print(f"Sent message '{message}'.")

    def receive_responses(self):
        for _ in self.messages:
            # receive the server responses to each of the sample messages from x-client through udp socket
            message, _ = self.udp_socket.recvfrom(BUFF_SIZE)
            # decode and print each of the received messages
            print(f"Received message '{message.decode()}'")

    def start(self):
        # bind a udp socket to connect to x-client
        self.bind_udp()
        # receive an initialization message from x-client
        self.get_xclient_init_message()
        # start sending and receiving the messages by typing the 'start' command
        if input() == "start":
            self.send_sample_packets()
            self.receive_responses()


if __name__ == "__main__":
    # start the client app program
    Client().start()
