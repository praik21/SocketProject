import socket

# Maximum size of the message to be echoed
ECHOMAX = 255  

def DieWithError(errorMessage):
    """Error handling function"""
    print(errorMessage)
    exit(1)

def main():
    # Check if the server port is passed as an argument
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <UDP SERVER PORT>")
        exit(1)

    echoServPort = int(sys.argv[1])  # First argument: local port to listen on

    # Create a UDP socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        DieWithError(f"server: socket() failed: {e}")

    # Bind the socket to the server address (IP and Port)
    try:
        sock.bind(('', echoServPort))
    except socket.error as e:
        DieWithError(f"server: bind() failed: {e}")

    print(f"server: Listening on port {echoServPort}")

    while True:
        # Wait for a message from the client
        try:
            message, clientAddress = sock.recvfrom(ECHOMAX)
            print(f"server: received string ``{message.decode()}`` from client on IP address {clientAddress[0]}")
        except socket.error as e:
            DieWithError(f"server: recvfrom() failed: {e}")

        # Echo the message back to the client
        try:
            sent = sock.sendto(message, clientAddress)
            if sent != len(message):
                DieWithError("server: sendto() sent a different number of bytes than expected")
        except socket.error as e:
            DieWithError(f"server: sendto() failed: {e}")

if __name__ == "__main__":
    main()
