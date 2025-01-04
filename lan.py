import socket
import threading

status = None


def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[{address}] {message}")
            client_socket.send("Move received.".encode('utf-8'))
        except ConnectionResetError:
            break
    print(f"[DISCONNECTED] {address} disconnected.")
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)
    print("[STARTING] Server is starting...")
    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))
    print("[CONNECTED] Connected to the server.")
    message = ''

    try:
        while True:
            client.send(message.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            print(f"Server: {response}")
    except KeyboardInterrupt:
        print("\n[DISCONNECTED] Exiting...")
    finally:
        client.close()


def start_lan(current_status):
    global status

    current_status = status
    if current_status == 'SERVER':
            start_server()
    else:
        start_client()

if __name__ == "__main__":
    start_lan()