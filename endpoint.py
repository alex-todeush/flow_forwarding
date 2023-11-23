import socket
import sys
import threading
import time
import hashlib


message_timers = {}

host_name = socket.gethostname()
my_ip_address = socket.gethostbyname(host_name)

def sender(name, goal_destination):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_address = ('<broadcast>', 54321)
    message_body = f"Hello from {name}:{my_ip_address}"
    # HEADER FORMAT (source_IP, device_name, operation, goal_destination, origin_IP, body)
    header = f"{my_ip_address},{name},request,{goal_destination},{my_ip_address},{message_body}"
    client_socket.sendto(header.encode(), broadcast_address)

    start_timer(hash_message_body(message_body))

def receiver():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((my_ip_address, 54321))

    while True:
        data, addr = server_socket.recvfrom(1024)
        source_ip, device_name, operation, goal_destination, origin, body = data.decode().split(',')

        if origin == my_ip_address:
            pass
        else:
            if operation == "confirmation":
                print(f"Acknowledgement for: {body}")
                cancel_timer(hash_message_body(body))
            elif operation == "forward":
                print(f"Received UDP packet from {origin}: {body}")

def hash_message_body(message_body):
    return hashlib.sha256(message_body.encode()).hexdigest()

def start_timer(message_body_hash):
    message_timers[message_body_hash] = threading.Timer(5, timeout_handler, args=[message_body_hash])
    message_timers[message_body_hash].start()

def cancel_timer(message_body_hash):
    if message_body_hash in message_timers:
        message_timers[message_body_hash].cancel()
        del message_timers[message_body_hash]

def timeout_handler(message_body_hash):
    print(f"No confirmation received for message with hash: {message_body_hash} within 5 seconds.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python3 client.py <name> <goal_destination>')
        sys.exit(1)

    name = sys.argv[1]
    goal_destination = sys.argv[2]

    server_thread = threading.Thread(target=receiver, args=())
    server_thread.start()
    
    sender(name, goal_destination)
    server_thread.join()
