#! /usr/bin/env python3

import socket

def udp_broadcast_listener(listen_port, response_message, response_port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow the socket to reuse addresses
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the listen port
    sock.bind(('', listen_port))

    print(f"Listening for UDP broadcasts on port {listen_port}")

    while True:
        # Receive data from the socket
        data, addr = sock.recvfrom(1024)
        print(f"Received message: {data} from {addr}")

        # Respond with a message
        response = response_message.encode('utf-8')
        sock.sendto(response, (addr[0], response_port))
        print(f"Sent response: {response_message} to {addr}")

if __name__ == "__main__":
    LISTEN_PORT = 12345        # Port to listen for broadcasts
    RESPONSE_MESSAGE = "Hello, this is a response from the server!"  # Response message
    RESPONSE_PORT = 12345      # Port to send the response to

    udp_broadcast_listener(LISTEN_PORT, RESPONSE_MESSAGE, RESPONSE_PORT)
