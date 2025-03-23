import argparse
from sender import Sender
from receiver import Receiver


class Client:
    """A client that can either send a file to a server or query a file from the server."""
    def __init__(self, listen_port, server_port, server_ip, query, filename):
        """
        Initialize the client with the specified parameters.

        :param listen_port: Port number for the client to listen on for incoming packets.
        :param server_port: Port number of the server to connect to.
        :param server_ip: IP address of the server.
        :param query: Boolean flag indicating if the client should query the server for a file.
        :param filename: Name of the file to send to the server or query from the server.
        """
        self.listen_port = listen_port
        self.server_port = server_port
        self.server_ip = server_ip
        self.query = query
        self.filename = filename
        self.reassembled_data = b''

    def run(self):
        """Execute the client's main functionality."""
        if self.query:
            self.query_file()
        else:
            self.send_file()
    
    def send_file(self):
        """
        Sends a file to the server.

        Reads the file specified by the class variable filename into a byte string,
        sends the filename to the server, and then sends the file data to the server.
        Ensures that an ACK is received from the server after sending the filename.
        """

        with open(self.filename, 'rb') as f:
            data = f.read()

        sender = Sender(self.server_ip, self.server_port, self.listen_port, filename)
        sender.send_data()
        sender.sock.close()

        sender = Sender(self.server_ip, self.server_port, self.listen_port, data)
        sender.send_data()

    def query_file(self):
        """
        Queries the server for a file and writes the received data to a local file.

        Sends a filename to the server, receives the file data from the server,
        and writes the received data to a local file with the same name as the queried file.
        Ensures that an ACK is received from the server after sending the filename, and sends
        ACKs as the data is received from the Server
        """
        sender = Sender(self.server_ip, self.server_port, self.listen_port, filename+"QUERY")
        sender.send_data()
        sender.sock.close()

        receiver = Receiver(self.listen_port, "127.0.0.1")
        receiver.start_receiving()
        self.reassembled_data = receiver.reassemble_data()
        with open("Client_files/" + self.filename, "wb") as f:
                f.write(self.reassembled_data)


if __name__ == "__main__":
    """Parse command-line arguments and start the Client."""
    parser = argparse.ArgumentParser(description="Client")
    parser.add_argument("--listen-port", type=int, required=True, help="Client's listening port")
    parser.add_argument("--server-port", type=int, required=True, help="Client's sending port")
    parser.add_argument("--server-ip", type=str, default="127.0.0.1", help="IP address of the server")
    parser.add_argument("-q", "--query", action="store_true", help="Query mode")
    args = parser.parse_args()

    filename = input("Enter the filename: ")
    client = Client(args.listen_port, args.server_port, args.server_ip, args.query, filename)
    client.run()