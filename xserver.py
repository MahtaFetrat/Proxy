# create x-client

import socket
from threading import Thread
import multiprocessing as mp
from utils import parse_message, parse_header, add_header, acked_recv, acked_send

# IP of x-server
XSERVER_IP = 'localhost'
# port of x-server
XSERVER_PORT = 8080


# create a class to handle each client app
class ClientHandler(mp.Process):
    # initiate the buffer size for reading and receiving from the udp and tcp sockets
    UDP_BUFF_SIZE = 1024
    TCP_BUFF_SIZE = 2048

    def __init__(self, client_app_ip, client_app_port, server_app_ip, server_app_port, sending_tcp_socket,
                 receiving_tcp_socket):
        super(ClientHandler, self).__init__()
        # initialize the client and server app ips and ports
        self.client_app_addr = client_app_ip, client_app_port
        self.server_app_addr = server_app_ip, server_app_port
        # initialize the x-client's sending and receiving sockets
        self.sending_tcp_socket = sending_tcp_socket
        self.receiving_tcp_socket = receiving_tcp_socket

        # consider a udp socket for the transmissions between server app and x-server
        self.udp_socket = None

    # handle udp requests the server app
    def handle_udp_conn_recv(self):
        while True:
            # receive message from the server app through the udp socket up to the buffer size
            payload, _ = self.udp_socket.recvfrom(ClientHandler.UDP_BUFF_SIZE)
            # print the received message
            print(f"Received udp message '{payload}'.")
            # create a message by adding header containing client and server apps' addresses
            # to the server app message
            message = add_header(payload.decode(), self.client_app_addr, self.server_app_addr)
            # send the built message through  x-client's tcp connection and receive an
            # acknowledgement from it
            acked_send(message, self.receiving_tcp_socket, ClientHandler.TCP_BUFF_SIZE)

    # handle tcp requests from x-client
    def handle_tcp_conn_recv(self):
        while True:
            # receive messages from the x-client through the tcp socket
            message = acked_recv(self.sending_tcp_socket, ClientHandler.TCP_BUFF_SIZE)
            # take the payload of the message and remove the added header
            _, payload = parse_message(message)
            # send the payload to the proper server app through udp socket
            self.udp_socket.sendto(payload.encode(), self.server_app_addr)
            # print the sent message
            print(f"Sent udp message '{payload}'.")

    # create a udp connection to handle the transmissions between x-server and server app
    def create_udp_connection(self):
        udp_socket_name = None
        try:
            # create a udp socket and bind it to x-server ip and a free port
            self.udp_socket = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.udp_socket.bind((XSERVER_IP, 0))
            # take the name of the created udp socket
            udp_socket_name = self.udp_socket.getsockname()[1]
        except socket.error as e:
            # handle socket exceptions
            print("(Error) Error opening the UDP socket: {}".format(e))
            print("(Error) Cannot open the UDP socket {}:{} or bind to it".format(
                XSERVER_IP, udp_socket_name))
        else:
            print("Bind to the UDP socket {}:{}".format(
                XSERVER_IP, udp_socket_name))

    def run(self):
        # for each client app process, create a udp connection
        self.create_udp_connection()

        # handle the udp connection from server app in a thread
        Thread(target=self.handle_udp_conn_recv).start()
        # handle the tcp connection from x-client in another thread
        Thread(target=self.handle_tcp_conn_recv).start()


# create a XServer class
class XServer:
    # initiate the buffer size for reading and receiving from the sockets
    BUFF_SIZE = 1024

    def __init__(self):
        # consider a tcp socket for listening upcoming messages from x-client
        self.tcp_socket = None
        # create dictionaries to store the x-client's sending and receiving connections
        self.tcp_sending_conns = {}
        self.tcp_receiving_conns = {}

    def identify_connection(self, conn):
        # receive the first message from x-client trough the tcp socket
        message = acked_recv(conn, XServer.BUFF_SIZE)
        # split the message into its header and payload
        header, payload = parse_message(message)
        # obtain the connection address from th header
        conn_addr = parse_header(header)
        # return the connection address and the connection type(payload might be 'sending' or 'receiving')
        return conn_addr, payload

    def connection_duplex(self, conn_addr):
        return conn_addr in self.tcp_sending_conns and conn_addr in self.tcp_receiving_conns

    def handle_connections(self):
        while True:
            # accept connections from x-client to the tcp socket
            conn, _ = self.tcp_socket.accept()
            # identify the connection address and type of it (sending or receiving)
            conn_addr, send_recv = self.identify_connection(conn)
            # add each type of connection to the proper dictionary
            # (key= connection address, value= tcp socket)
            conn_dict = self.tcp_sending_conns if send_recv == "sending" else self.tcp_receiving_conns
            conn_dict[conn_addr] = conn

            # if there are sending and receiving connections for a specific client,
            # create a client handler process to handle it
            if self.connection_duplex(conn_addr):
                ClientHandler(*conn_addr, self.tcp_sending_conns[conn_addr],
                              self.tcp_receiving_conns[conn_addr]).start()

    # make a tcp socket and bind it to the x-server ip and port
    def create_listening_tcp_socket(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((XSERVER_IP, XSERVER_PORT))
        print(f"Listening TCP on {XSERVER_IP}:{XSERVER_PORT}")
        self.tcp_socket.listen()

    # start by creating a tcp socket and handling the connections
    def start(self):
        self.create_listening_tcp_socket()
        self.handle_connections()


if __name__ == "__main__":
    # start the x-server program
    XServer().start()
