# create x-server

import socket
import argparse
import sys
import time
from threading import Thread
import multiprocessing as mp
from utils import add_header, parse_message, acked_send, acked_recv

# IP of x-client
IP = 'localhost'
# IP of x-server
XSERVER_IP = 'localhost'
# port of x-server
XSERVER_PORT = 8080


# create a class to handle each client app
class ClientHandler(mp.Process):
    # initiate the buffer size for reading and receiving from the udp and tcp sockets
    UDP_BUFF_SIZE = 1024
    TCP_BUFF_SIZE = 2048

    def __init__(self, client_app_ip, client_app_port, server_app_ip, server_app_port):
        super(ClientHandler, self).__init__()
        # initialize the client and server app ips and ports
        self.client_app_addr = client_app_ip, client_app_port
        self.server_app_addr = server_app_ip, server_app_port

        # consider a udp socket for the transmissions between each client app and x-client
        self.listening_udp_socket = None
        # consider sending and receiving tcp sockets for each client app
        self.sending_tcp_socket = None
        self.receiving_tcp_socket = None

    # handle udp requests the client app
    def handle_udp_conn_recv(self):
        while True:
            # receive message from the client app through the udp socket up to buffer size
            payload, _ = self.listening_udp_socket.recvfrom(ClientHandler.UDP_BUFF_SIZE)
            # print the received message
            print(f"Received udp message '{payload}'.")
            # create a message by adding header containing client and server apps' addresses
            # to the client app message
            message = add_header(payload.decode(), self.client_app_addr, self.server_app_addr)
            # send the built message through sending tcp connection and receive an
            # acknowledgement from it
            acked_send(message, self.sending_tcp_socket, ClientHandler.TCP_BUFF_SIZE)

    # handle tcp messages from x-server
    def handle_tcp_conn_recv(self):
        while True:
            # receive messages from the x-server through the tcp socket
            message = acked_recv(self.receiving_tcp_socket, ClientHandler.TCP_BUFF_SIZE)
            # take the payload of the message and remove the added header
            _, payload = parse_message(message)
            # send the payload to the proper client app through udp socket
            self.listening_udp_socket.sendto(payload.encode(), self.client_app_addr)
            # print the sent message
            print(f"Sent udp message '{payload}'.")

    # create a udp connection to handle the transmissions between x-client and client app
    def create_udp_connection(self):
        udp_socket_name = None
        try:
            # create a udp socket and bind it to x-client ip and a free port
            self.listening_udp_socket = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.listening_udp_socket.bind((IP, 0))
            # take the name of the created udp socket
            udp_socket_name = self.listening_udp_socket.getsockname()[1]
            self.listening_udp_socket.sendto(str(udp_socket_name).encode(), self.client_app_addr)
        except socket.error as e:
            # handle socket exceptions
            print("(Error) Error opening the UDP socket: {}".format(e))
            print("(Error) Cannot open the UDP socket {}:{} or bind to it".format(
                IP, udp_socket_name))
        else:
            print("Bind to the UDP socket {}:{}".format(IP, udp_socket_name))

    # create tcp connection for each client app to send messages to x-server
    def create_sending_tcp_connection(self):
        try:
            # make a tcp socket
            self.sending_tcp_socket = socket.socket()
            # connect the tcp socket to x-server
            self.sending_tcp_socket.connect((XSERVER_IP, XSERVER_PORT))
            # create an initialization message
            payload = "sending"
            # add a header containing client and server apps' addresses to the message
            message = add_header(payload, self.client_app_addr, self.server_app_addr)
            # send the initialization message to x-server trough the tcp sending socket
            acked_send(message, self.sending_tcp_socket, ClientHandler.TCP_BUFF_SIZE)
        except socket.error as e:
            # handle socket exceptions
            print("(Error) Error opening the sending TCP socket: {}.".format(e))
            print("(Error) Cannot connect sending TCP socket to {}:{}.".format(
                XSERVER_IP, XSERVER_PORT))
            sys.exit(1)
        else:
            print("Connected the TCP socket to {}:{}.".format(
                XSERVER_IP, XSERVER_PORT))

    # create tcp connection for each client app to receive messages from x-server
    def create_receiving_tcp_connection(self):
        try:
            # make a tcp socket
            self.receiving_tcp_socket = socket.socket()
            # connect the tcp socket to x-server
            self.receiving_tcp_socket.connect((XSERVER_IP, XSERVER_PORT))
            # create an initialization message
            payload = "receiving"
            # add a header containing client and server apps' addresses to the message
            message = add_header(payload, self.client_app_addr, self.server_app_addr)
            # send the initialization message to x-server trough the tcp sending socket
            acked_send(message, self.receiving_tcp_socket, ClientHandler.TCP_BUFF_SIZE)
        except socket.error as e:
            # handle socket exceptions
            print("(Error) Error opening the receiving TCP socket: {}".format(e))
            print("(Error) Cannot connect receiving TCP socket to {}:{}.".format(
                XSERVER_IP, XSERVER_PORT))
        else:
            print("Connected the TCP socket to {}:{}.".format(
                XSERVER_IP, XSERVER_PORT))

    def run(self):
        # for each client app process, create a udp connection
        self.create_udp_connection()

        # for each client app, create sending and receiving tcp connections
        self.create_sending_tcp_connection()
        self.create_receiving_tcp_connection()

        # handle the udp connection from client app in a thread
        Thread(target=self.handle_udp_conn_recv).start()
        # handle the tcp connection to the x-server in another thread
        Thread(target=self.handle_tcp_conn_recv).start()


# create a XClient class
class XClient:
    def __init__(self):
        self.args = None

    # take and parse arguments as input
    def parse_input_argument(self):
        parser = argparse.ArgumentParser(
            description='This is the x-client program that creates a tunnel to the server over TCP connection.'
        )

        parser.add_argument(
            '-ut',
            '--udp-tunnel',
            action='append',
            required=True,
            help="Specify client and server app addresses. The format is 'client ip:client port:server ip:server port'."
        )

        self.args = parser.parse_args()

    # for each client app take the ip and port of client and server apps
    def start_processes(self):
        for tun_addr in self.args.udp_tunnel:
            client_app_ip = tun_addr.split(':')[0]
            client_app_port = int(tun_addr.split(':')[1])
            server_app_ip = tun_addr.split(':')[2]
            server_app_port = int(tun_addr.split(':')[3])

            # for each client create a client handler process to handle it
            ClientHandler(client_app_ip, client_app_port,
                          server_app_ip, server_app_port).start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Closing the connections...")

    # start by parsing the input arguments and stating  processes for each client app
    def start(self):
        self.parse_input_argument()
        self.start_processes()


if __name__ == "__main__":
    # start the x-client program
    XClient().start()
