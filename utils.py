def parse_message(message):
    header = message.split('\n')[0]
    payload = ''.join(message.split('\n')[1:])
    return header, payload


def parse_header(header):
    header_args = header.split(':')
    return header_args[0], int(header_args[1]), header_args[2], int(header_args[3])


def add_header(payload, client_app_addr, server_app_addr):
    header = "{}:{}:{}:{}\n".format(*client_app_addr, *server_app_addr)
    return header + payload


def acked_send(message, socket, buff_size):
    print(f"Sent tcp message '{message}'.")
    socket.send(message.encode())
    socket.recv(buff_size)


def acked_recv(socket, buff_size):
    message = socket.recv(buff_size).decode()
    print(f"Received tcp message '{message}'.")
    socket.send("ACK".encode())
    return message
