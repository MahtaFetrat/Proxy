# create a server app program

import socket

# IP of the server app
IP = 'localhost'

# initiate the buffer size for reading and receiving from the sockets
BUFF_SIZE = 1024


# create a Server class representing the server app
class Server:
    def __init__(self):
        # consider a udp socket for the transmissions between server app and x-server
        self.udp_socket = None

    def bind_udp(self):
        # create the udp socket for the transmissions between server app and x-server
        self.udp_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # bind the udp socket to a free port
        self.udp_socket.bind((IP, 0))
        # get the port assigned to the udp socket and print it
        udp_socket_name = self.udp_socket.getsockname()[1]
        print(f"Listening UDP on {IP}:{udp_socket_name}")

    # create a sample method that builds the server responses
    @staticmethod
    def build_response(message):
        # this server app is supposed to convert the received messages to uppercase
        # and return it to the client app
        return message.upper()

    def handle_requests(self):
        while True:
            # receive messages from x-server up tp buffer size
            message, addr = self.udp_socket.recvfrom(BUFF_SIZE)
            # print the received message
            print(f"Received message '{message}'.")
            # build the response for each received message
            response = self.build_response(message.decode())
            # send the built response to x-server through the udp socket
            self.udp_socket.sendto(response.encode(), addr)
            # print the sent response
            print(f"Sent message '{response}'.")

    # start the server app job by creating a udp connection and handle the q through it
    def start(self):
        self.bind_udp()
        self.handle_requests()


if __name__ == "__main__":
    # start the server app program
    Server().start()
