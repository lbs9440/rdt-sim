import argparse
from sender import Sender
from receiver import Receiver

class Server:
    """A server that can receive files from a client or respond to file queries."""
    def __init__(self, server_port, server_ip):
        """
        Initialize the server with the specified parameters.

        :param server_port: Port number to listen on.
        :param server_ip: IP address of the server.
        """
        self.server_port = server_port
        self.server_ip = server_ip
        self.filename = ""
        self.reassembled_data = b''
        self.sender_address = None


    def run(self):
        """
        Receive a file from a client or respond to a file query.

        If the server is receiving a file, it writes the received data to a local file.
        If the server is responding to a file query, it sends the file data to the client.
        """
        receiver = Receiver(self.server_port, self.server_ip)
        receiver.start_receiving()
        self.filename = receiver.return_filename()

        if self.filename.endswith("QUERY"):
            with open("Server_files/" + self.filename.removesuffix("QUERY"), "rb") as f:
                data = f.read()
            self.sender_address = receiver.sender_address
            sender = Sender(self.sender_address[0], self.sender_address[1], self.server_port, data)
            sender.send_data()

        else:
            receiver = Receiver(self.server_port, self.server_ip)
            receiver.start_receiving()
            self.reassembled_data = receiver.reassemble_data()
            with open("Server_files/" + server.filename, "wb") as f:
                f.write(server.reassembled_data)

if __name__ == "__main__":
    """Parse command-line arguments and start the Server."""
    parser = argparse.ArgumentParser(description="Server")
    parser.add_argument("--server-port", type=int, required=True, help="Server's sending port")
    parser.add_argument("--server-ip", type=str, default="127.0.0.1", help="Client's listening port")
    args = parser.parse_args()

    server = Server(args.server_port, args.server_ip)
    server.run()
    
