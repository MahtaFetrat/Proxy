import socket
from threading import Thread
import multiprocessing as mp
from utils import parse_message, parse_header, add_header, acked_recv, acked_send

XSERVER_IP = 'localhost'
XSERVER_PORT = 8080


class ClientHandler(mp.Process):
    UDP_BUFF_SIZE = 1024
    TCP_BUFF_SIZE = 2048

    def __init__(self, client_app_ip, client_app_port, server_app_ip, server_app_port, sending_tcp_socket,
                 receiving_tcp_socket):
        super(ClientHandler, self).__init__()
        self.client_app_addr = client_app_ip, client_app_port
        self.server_app_addr = server_app_ip, server_app_port
        self.sending_tcp_socket = sending_tcp_socket
        self.receiving_tcp_socket = receiving_tcp_socket

        self.udp_socket = None

    def handle_udp_conn_recv(self):
        while True:
            payload, _ = self.udp_socket.recvfrom(ClientHandler.UDP_BUFF_SIZE)
            print(f"Received udp message '{payload}'.")
            message = add_header(payload.decode(), self.client_app_addr, self.server_app_addr)
            acked_send(message, self.receiving_tcp_socket, ClientHandler.TCP_BUFF_SIZE)

    def handle_tcp_conn_recv(self):
        while True:
            message = acked_recv(self.sending_tcp_socket, ClientHandler.TCP_BUFF_SIZE)
            _, payload = parse_message(message)
            self.udp_socket.sendto(payload.encode(), self.server_app_addr)
            print(f"Sent udp message '{payload}'.")

    def create_udp_connection(self):
        udp_socket_name = None
        try:
            self.udp_socket = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.udp_socket.bind((XSERVER_IP, 0))
            udp_socket_name = self.udp_socket.getsockname()[1]
        except socket.error as e:
            print("(Error) Error opening the UDP socket: {}".format(e))
            print("(Error) Cannot open the UDP socket {}:{} or bind to it".format(
                XSERVER_IP, udp_socket_name))
        else:
            print("Bind to the UDP socket {}:{}".format(
                XSERVER_IP, udp_socket_name))

    def run(self):
        self.create_udp_connection()

        Thread(target=self.handle_udp_conn_recv).start()
        Thread(target=self.handle_tcp_conn_recv).start()


class XServer:
    BUFF_SIZE = 1024

    def __init__(self):
        self.tcp_socket = None
        self.tcp_sending_conns = {}
        self.tcp_receiving_conns = {}

    def identify_connection(self, conn):
        message = acked_recv(conn, XServer.BUFF_SIZE)
        header, payload = parse_message(message)
        conn_addr = parse_header(header)
        return conn_addr, payload

    def connection_duplex(self, conn_addr):
        return conn_addr in self.tcp_sending_conns and conn_addr in self.tcp_receiving_conns

    def handle_connections(self):
        while True:
            conn, _ = self.tcp_socket.accept()
            conn_addr, send_recv = self.identify_connection(conn)
            conn_dict = self.tcp_sending_conns if send_recv == "sending" else self.tcp_receiving_conns
            conn_dict[conn_addr] = conn

            if self.connection_duplex(conn_addr):
                ClientHandler(*conn_addr, self.tcp_sending_conns[conn_addr],
                              self.tcp_receiving_conns[conn_addr]).start()

    def create_listening_tcp_socket(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((XSERVER_IP, XSERVER_PORT))
        print(f"Listening TCP on {XSERVER_IP}:{XSERVER_PORT}")
        self.tcp_socket.listen()

    def start(self):
        self.create_listening_tcp_socket()
        self.handle_connections()


if __name__ == "__main__":
    XServer().start()
