import socket
import sys

host_name = socket.gethostname()
my_ip_address = socket.gethostbyname(host_name)

def udp_client(port):
    print(host_name)
    print(my_ip_address)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    server_address = ('<broadcast>', port)

    while True:
        header = "endpoint"
        client_socket.sendto(header.encode('utf-8'), server_address)
        response, _ = client_socket.recvfrom(1024)
        print('Server response: "{}"'.format(response.decode('utf-8')))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python client.py <port>')
        sys.exit(1)

    port = int(sys.argv[1])

    udp_client(port)
