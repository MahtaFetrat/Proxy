# create utility functions

# take a message and split it into header and payload
def parse_message(message):
    header = message.split('\n')[0]
    payload = ''.join(message.split('\n')[1:])
    return header, payload


# take a header and return the IP and port values in this format:
# sender-ip, sender-port, receiver_ip, receiver_port
def parse_header(header):
    header_args = header.split(':')
    return header_args[0], int(header_args[1]), header_args[2], int(header_args[3])


# make a header including the client and server addresses
# then make a packet containing the made header and payload
def add_header(payload, client_app_addr, server_app_addr):
    header = "{}:{}:{}:{}\n".format(*client_app_addr, *server_app_addr)
    return header + payload


# take a message and send it through a given socket. then receive an acknowledgement up to buffer size
def acked_send(message, socket, buff_size):
    print(f"Sent tcp message '{message}'.")
    socket.send(message.encode())
    socket.recv(buff_size)


# take a socket and receive messages from it up to buffer size. them send an acknowledgement
def acked_recv(socket, buff_size):
    message = socket.recv(buff_size).decode()
    print(f"Received tcp message '{message}'.")
    socket.send("ACK".encode())
    return message
