import socket
import sys
import threading
import time
import hashlib

BUFF_SIZE = 980
message_timers = {}
host_name = socket.gethostname()
my_ip_address = socket.gethostbyname(host_name)

def sender(name, goal_destination, msg_type, msg_body):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    broadcast_address = ('<broadcast>', 54321)
    if msg_type == "text":
        message_body = msg_body
        # HEADER FORMAT (source_IP, device_name, operation, goal_destination, origin_IP, body)
        header = f"{my_ip_address},{name},REQ,{goal_destination},{my_ip_address},'{message_body}'"
        client_socket.sendto(header.encode(), broadcast_address)
        start_timer(hash_message_body(message_body))
    elif msg_type == "file":
        with open(msg_body, 'rb') as file:
             while True:
                message_body = file.read(BUFF_SIZE)
                if not message_body:
                    break
                # HEADER FORMAT (source_IP, device_name, operation, goal_destination, origin_IP, body)
                header = f"{my_ip_address},{name},REQ,{goal_destination},{my_ip_address},{message_body}"
                client_socket.sendto(header.encode(), broadcast_address)
                #start_timer(hash_message_body(str(message_body)))

def receiver():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((my_ip_address, 54321))

    while True:
        data, addr = server_socket.recvfrom(1024)
        source_ip, device_name, operation, goal_destination, origin, body = data.decode().split(',',5)

        if origin == my_ip_address:
            pass
        else:
            if operation == "ACK":
                print(f"Acknowledgement for: {hash_message_body(str(body))}")
                cancel_timer(hash_message_body(str(body)))
            elif operation == "FWD":
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
    print(f"No acknowledgment received for message with hash: {message_body_hash} within 5 seconds.")
    del message_timers[message_body_hash]

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print('Usage: python3 client.py <name> <goal_destination> <msg_type> <msg_body>')
        sys.exit(1)

    name = sys.argv[1]
    goal_destination = sys.argv[2]
    msg_type = sys.argv[3]
    msg_body = sys.argv[4]

    server_thread = threading.Thread(target=receiver, args=())
    server_thread.start()
    
    sender(name, goal_destination, msg_type, msg_body)
    server_thread.join()
