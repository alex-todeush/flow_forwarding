import socket
import sys
import threading

host_name = socket.gethostname()
my_ip_address = socket.gethostbyname(host_name)

def udp_client(port, goal_destination):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_address = ('<broadcast>', port)
    message_body = f"Hello from {my_ip_address}"
    # HEADER FORMAT (source_IP, source_type, operation, goal_destination, origin_IP, body)
    header = f"{my_ip_address},endpoint,request,{goal_destination},{my_ip_address},{message_body}"
    client_socket.sendto(header.encode(), broadcast_address)
    response, _ = client_socket.recvfrom(1024)
    print(f'Server response: "{response.decode()}"')

def udp_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((my_ip_address, port))

    while True:
        data, addr = server_socket.recvfrom(1024)
        source_ip, source_type, operation, goal_destination, origin, body = data.decode().split(',')
        print(f"Received UDP packet from {origin}: {body}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python3 client.py <port> <goal_destination>')
        sys.exit(1)

    port = int(sys.argv[1])
    goal_destination = sys.argv[2]

    server_thread = threading.Thread(target=udp_server, args=(port,))
    server_thread.start()
    
    udp_client(port, goal_destination)
    server_thread.join()
