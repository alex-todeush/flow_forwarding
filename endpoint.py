import socket
import sys
import threading

host_name = socket.gethostname()
my_ip_address = socket.gethostbyname(host_name)

def udp_client(name, goal_destination):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_address = ('<broadcast>', 54321)
    message_body = f"Hello from {name}:{my_ip_address}"
    # HEADER FORMAT (source_IP, device_name, operation, goal_destination, origin_IP, body)
    header = f"{my_ip_address},{name},request,{goal_destination},{my_ip_address},{message_body}"
    client_socket.sendto(header.encode(), broadcast_address)
    #response, _ = client_socket.recvfrom(1024)
    #print(f'Server response: "{response.decode()}"')

def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((my_ip_address, 54321))

    while True:
        data, addr = server_socket.recvfrom(1024)
        source_ip, device_name, operation, goal_destination, origin, body = data.decode().split(',')
        if(origin == my_ip_address):
            pass
        else:
            if(operation == "confirmation"):
                print(f"acknowledgement for: {body}")
            elif(operation == "forward"):
                print(f"Received UDP packet from {origin}: {body}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python3 client.py <name> <goal_destination>')
        sys.exit(1)

    name = sys.argv[1]
    goal_destination = sys.argv[2]

    server_thread = threading.Thread(target=udp_server, args=())
    server_thread.start()
    
    udp_client(name, goal_destination)
    server_thread.join()
