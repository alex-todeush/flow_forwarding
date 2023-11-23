import socket
import sys
import ipaddress
import time

host_name = socket.gethostname()
my_ip_address = socket.gethostbyname(host_name)

def get_ip_addresses():
    return set([i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)])

def get_broadcast_address(ip_address):
    subnet_mask = "255.255.255.0"
    network = ipaddress.IPv4Network(f"{ip_address}/{subnet_mask}", strict=False)
    broadcast_address = network.network_address + (2 ** (32 - network.prefixlen)) - 1
    return broadcast_address

def print_forwarding_table(table):
    print("Forwarding Table:")
    print("{:<15} {:<15}".format("Destination", "Next Hop"))
    for destination, next_hop in table.items():
        print("{:<15} {:<15}".format(destination, next_hop))

def router(name):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    my_ips = get_ip_addresses()
    my_broadcasts = [get_broadcast_address(ip) for ip in my_ips]

    server_address = ('', 54321)
    server_socket.bind(server_address)

    print(f'UDP server is listening on {my_ips}')

    forwarding_table = {}
    device_list = {}
    last_seen_timestamps = {}

    while True:
        data, client_address = server_socket.recvfrom(1024)
        print(f'Received message: "{data.decode()}" from {client_address}')

        current_time = time.time()
        source_ip, device_name, operation, goal_destination, origin, body = data.decode().split(',')

        if operation == "request" and source_ip in last_seen_timestamps and current_time - last_seen_timestamps[source_ip] <= 2:
            # print(f"Ignoring message from {source_ip}. Already seen in the last 2 seconds.")
            pass
        else:
            forwarding_table[source_ip] = client_address[0]
            last_seen_timestamps[source_ip] = current_time
            device_list[device_name] = source_ip
            print_forwarding_table(forwarding_table)

            if goal_destination in device_list:
                # Send confirmation
                header = f"{my_ip_address},{name},confirmation,{origin},{my_ip_address},{body}"
                server_socket.sendto(header.encode(), (client_address[0], 54321))
                # Forward message
                header = f"{my_ip_address},router,forward,{goal_destination},{origin},{body}"
                server_socket.sendto(header.encode(), (device_list[goal_destination], 54321))
            else:
                if source_ip != my_ip_address:
                    for ip in my_broadcasts:
                        header = f"{my_ip_address},router,request,{goal_destination},{origin},{body}"
                        broadcast_address = (str(ip), 54321)
                        server_socket.sendto(header.encode(), broadcast_address)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python3 server.py <name>')
        sys.exit(1)

    name = sys.argv[1]
    router(name)
