def parse_message(message):
    header = message.split('\n')[0]
    payload = ''.join(message.split('\n')[1:])
    return header, payload

def parse_header(header):
    header_args = header.split(':')
    return tuple(header_args)
    
def add_header(payload, client_app_addr, server_app_addr):
    header = "{}:{}:{}:{}\n".format(*client_app_addr, *server_app_addr)
    return header + payload
