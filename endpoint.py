import socket
import sys

host_name = socket.gethostname()
my_ip_address = socket.gethostbyname(host_name)

def udp_client(port, goal_destination):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_address = ('<broadcast>', port)
    # HEADER FORMAT (source_IP, source_type, operation, goal_destination, placeholder)
    header = f"{my_ip_address},endpoint,request,{goal_destination},placeholder"
    client_socket.sendto(header.encode(), broadcast_address)
    response, _ = client_socket.recvfrom(1024)
    print(f'Server response: "{response.decode()}"')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python3 client.py <port> <goal_destination>')
        sys.exit(1)

    port = int(sys.argv[1])
    goal_destination = sys.argv[2]
    udp_client(port, goal_destination)
