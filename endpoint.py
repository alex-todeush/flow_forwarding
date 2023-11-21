import socket
import sys

host_name = socket.gethostname()
my_ip_address = socket.gethostbyname(host_name)

def udp_client(port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_address = ('<broadcast>', port)
    header = f"{my_ip_address},endpoint"
    print(header)
    client_socket.sendto(header.encode(), broadcast_address)
    response, _ = client_socket.recvfrom(1024)
    print(f'Server response: "{response.decode()}"')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python client.py <port>')
        sys.exit(1)

    port = int(sys.argv[1])
    udp_client(port)
