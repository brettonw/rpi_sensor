#! /usr/bin/env python3

import socket
import time

def find_devices_on_network(broadcast_message, listen_port, broadcast_port, timeout=5):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow the socket to send broadcast messages
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Bind the socket to the listen port
    sock.bind(('', listen_port))
    # Set a timeout for receiving responses
    sock.settimeout(timeout)

    # Broadcast message
    message = broadcast_message.encode('utf-8')
    broadcast_address = ('<broadcast>', broadcast_port)
    sock.sendto(message, broadcast_address)
    print(f"Broadcast message '{broadcast_message}' sent on port {broadcast_port}")

    devices = []
    start_time = time.time()

    while True:
        try:
            # Receive response from devices
            data, addr = sock.recvfrom(1024)
            response_time = time.time() - start_time
            devices.append((addr[0], data.decode('utf-8'), response_time))
            print(f"Received response from {addr[0]}: {data.decode('utf-8')} (response time: {response_time:.2f} seconds)")
        except socket.timeout:
            # Exit the loop when timeout occurs
            break

    sock.close()
    return devices

if __name__ == "__main__":
    BROADCAST_MESSAGE = "Discovery: Who is out there?"  # Message to broadcast
    LISTEN_PORT = 50001  # Port to listen for responses
    BROADCAST_PORT = 50000  # Port to send the broadcast message
    TIMEOUT = 10  # Time to wait for responses

    devices = find_devices_on_network(BROADCAST_MESSAGE, LISTEN_PORT, BROADCAST_PORT, TIMEOUT)

    if devices:
        print("Devices found on the network:")
        for device in devices:
            print(f"IP: {device[0]}, Response: {device[1]}, Response Time: {device[2]:.2f} seconds")
    else:
        print("No devices responded to the broadcast.")
