import socket
import sys

def router(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    server_address = ('', port)
    server_socket.bind(server_address)

    print('UDP server is listening on port {}'.format(port))

    while True:
        data, client_address = server_socket.recvfrom(1024)
        print('Received message: "{}" from {}'.format(data.decode(), client_address))

        response = 'Server received your message'
        server_socket.sendto(response.encode(), (client_address))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python server.py <port>')
        sys.exit(1)

    port = int(sys.argv[1])
    router(port)
