import socket
import sys

ECHOMAX = 255  # Longest string to echo
ITERATIONS = 5  # Number of iterations the client executes

def DieWithError(errorMessage):
    """Error handling function"""
    print(errorMessage)
    sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <Server IP address> <Echo Port>")
        sys.exit(1)

    servIP = sys.argv[1]  # First arg: server IP address (dotted decimal)
    echoServPort = int(sys.argv[2])  # Second arg: server port

    print(f"client: Arguments passed: server IP {servIP}, port {echoServPort}")

    # Create a UDP socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        DieWithError(f"client: socket() failed: {e}")

    # Server address
    echoServAddr = (servIP, echoServPort)

    print(f"client: Echoing strings for {ITERATIONS} iterations")

    for i in range(ITERATIONS):
        # Get user input
        echoString = input("\nEnter string to echo: ")
        if not echoString:
            DieWithError("client: error reading string to echo")

        print(f"\nclient: reads string ``{echoString}''")

        try:
            # Send the string to the server
            sock.sendto(echoString.encode(), echoServAddr)

            # Receive the echoed response from the server
            data, fromAddr = sock.recvfrom(ECHOMAX)
            respString = data.decode()

            if fromAddr[0] != servIP:
                DieWithError("client: Error: received a packet from unknown source.")
                
            print(f"client: received string ``{respString}'' from server on IP address {fromAddr[0]}")
        except socket.error as e:
            DieWithError(f"client: error during communication: {e}")

    # Close the socket
    sock.close()

if __name__ == "__main__":
    main()
