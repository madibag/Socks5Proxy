import socket
import threading

def handle_client(client_socket):
    # Receive the SOCKS5 handshake message
    handshake = client_socket.recv(1024)
    
    # Send the SOCKS5 handshake response
    client_socket.send(b'\x05\x00')
    
    # Receive the SOCKS5 request message
    request = client_socket.recv(1024)
    
    # Extract the target address and port from the request message
    address_type = request[3]
    if address_type == 1:
        target_address = socket.inet_ntoa(request[4:8])
        target_port = int.from_bytes(request[8:], 'big')
    elif address_type == 3:
        target_address_length = request[4]
        target_address = request[5:5+target_address_length].decode()
        target_port = int.from_bytes(request[5+target_address_length:], 'big')
    else:
        # Unsupported address type
        client_socket.close()
        return
    
    # Connect to the target server
    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_socket.connect((target_address, target_port))
    
    # Send the SOCKS5 response message
    response = b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + b'\x00\x00'
    client_socket.send(response)
    
    # Start forwarding data between the client and the target server
    client_thread = threading.Thread(target=forward_data, args=(client_socket, target_socket))
    target_thread = threading.Thread(target=forward_data, args=(target_socket, client_socket))
    client_thread.start()
    target_thread.start()

def forward_data(source_socket, destination_socket):
    while True:
        data = source_socket.recv(4096)
        if not data:
            break
        destination_socket.sendall(data)
    source_socket.close()
    destination_socket.close()

def start_server():
    # Create a SOCKS5 proxy server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 1080))
    server_socket.listen(10)

    local_addr, local_port = server_socket.getsockname()
    print(f"Proxy server running at {local_addr}:{local_port}")
    
    # Accept incoming client connections
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    start_server()
