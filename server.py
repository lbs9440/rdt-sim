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


    def run(self):
        receiver = Receiver(self.server_port, self.server_ip)
        receiver.start_receiving()
        self.filename = receiver.return_filename()

        receiver = Receiver(self.server_port, self.server_ip)
        receiver.start_receiving()
        self.reassembled_data = receiver.reassemble_data()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server")
    parser.add_argument("--server-port", type=int, required=True, help="Server's sending port")
    parser.add_argument("--server-ip", type=str, default="127.0.0.1", help="Client's listening port")
    args = parser.parse_args()

    server = Server(args.server_port, args.server_ip)
    server.run()
    # after it  runs call resemble data and wb to a new file in Server_files
    with open("Server_files/" + server.filename, "wb") as f:
        f.write(server.reassembled_data)
