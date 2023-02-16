import socket
import argparse
import sys
import time
from threading import Thread
import multiprocessing as mp
from utils import add_header, parse_message, acked_send, acked_recv

IP = 'localhost'
XSERVER_IP = 'localhost'
XSERVER_PORT = 8080


class ClientHandler(mp.Process):
    UDP_BUFF_SIZE = 1024
    TCP_BUFF_SIZE = 2048

    def __init__(self, client_app_ip, client_app_port, server_app_ip, server_app_port):
        super(ClientHandler, self).__init__()
        self.client_app_addr = client_app_ip, client_app_port
        self.server_app_addr = server_app_ip, server_app_port

        self.listening_udp_socket = None
        self.sending_tcp_socket = None
        self.receiving_tcp_socket = None

    def handle_udp_conn_recv(self):
        while True:
            payload, _ = self.listening_udp_socket.recvfrom(ClientHandler.UDP_BUFF_SIZE)
            print(f"Received udp message '{payload}'.")
            message = add_header(payload.decode(), self.client_app_addr, self.server_app_addr)
            acked_send(message, self.sending_tcp_socket, ClientHandler.TCP_BUFF_SIZE)

    def handle_tcp_conn_recv(self):
        while True:
            message = acked_recv(self.receiving_tcp_socket, ClientHandler.TCP_BUFF_SIZE)
            _, payload = parse_message(message)
            self.listening_udp_socket.sendto(payload.encode(), self.client_app_addr)
            print(f"Sent udp message '{payload}'.")

    def create_udp_connection(self):
        udp_socket_name = None
        try:
            self.listening_udp_socket = socket.socket(
                family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.listening_udp_socket.bind((IP, 0))
            udp_socket_name = self.listening_udp_socket.getsockname()[1]
            self.listening_udp_socket.sendto(str(udp_socket_name).encode(), self.client_app_addr)
        except socket.error as e:
            print("(Error) Error opening the UDP socket: {}".format(e))
            print("(Error) Cannot open the UDP socket {}:{} or bind to it".format(
                IP, udp_socket_name))
        else:
            print("Bind to the UDP socket {}:{}".format(IP, udp_socket_name))

    def create_sending_tcp_connection(self):
        try:
            self.sending_tcp_socket = socket.socket()
            self.sending_tcp_socket.connect((XSERVER_IP, XSERVER_PORT))
            payload = "sending"
            message = add_header(payload, self.client_app_addr, self.server_app_addr)
            acked_send(message, self.sending_tcp_socket, ClientHandler.TCP_BUFF_SIZE)
        except socket.error as e:
            print("(Error) Error opening the sending TCP socket: {}.".format(e))
            print("(Error) Cannot connect sending TCP socket to {}:{}.".format(
                XSERVER_IP, XSERVER_PORT))
            sys.exit(1)
        else:
            print("Connected the TCP socket to {}:{}.".format(
                XSERVER_IP, XSERVER_PORT))

    def create_receiving_tcp_connection(self):
        try:
            self.receiving_tcp_socket = socket.socket()
            self.receiving_tcp_socket.connect((XSERVER_IP, XSERVER_PORT))
            payload = "receiving"
            message = add_header(payload, self.client_app_addr, self.server_app_addr)
            acked_send(message, self.receiving_tcp_socket, ClientHandler.TCP_BUFF_SIZE)
        except socket.error as e:
            print("(Error) Error opening the receiving TCP socket: {}".format(e))
            print("(Error) Cannot connect receiving TCP socket to {}:{}.".format(
                XSERVER_IP, XSERVER_PORT))
        else:
            print("Connected the TCP socket to {}:{}.".format(
                XSERVER_IP, XSERVER_PORT))

    def run(self):
        self.create_udp_connection()
        self.create_sending_tcp_connection()
        self.create_receiving_tcp_connection()

        Thread(target=self.handle_udp_conn_recv).start()
        Thread(target=self.handle_tcp_conn_recv).start()


class XClient:
    def __init__(self):
        self.args = None

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

    def start_processes(self):
        for tun_addr in self.args.udp_tunnel:
            client_app_ip = tun_addr.split(':')[0]
            client_app_port = int(tun_addr.split(':')[1])
            server_app_ip = tun_addr.split(':')[2]
            server_app_port = int(tun_addr.split(':')[3])

            ClientHandler(client_app_ip, client_app_port,
                          server_app_ip, server_app_port).start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Closing the connections...")

    def start(self):
        self.parse_input_argument()
        self.start_processes()


if __name__ == "__main__":
    XClient().start()
