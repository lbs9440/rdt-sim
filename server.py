import argparse
import threading
from sender import Sender
from receiver import Receiver
import os
import struct
import time

class Server:
    def __init__(self, server_port, server_ip):
        self.server_port = server_port
        self.server_ip = server_ip
        self.filename = ""
        self.reassembled_data = b''
        self.sender_address = None


    def run(self):
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
    parser = argparse.ArgumentParser(description="Server")
    parser.add_argument("--server-port", type=int, required=True, help="Server's sending port")
    parser.add_argument("--server-ip", type=str, default="127.0.0.1", help="Client's listening port")
    args = parser.parse_args()

    server = Server(args.server_port, args.server_ip)
    server.run()
    
