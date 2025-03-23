import argparse
import threading
from sender import Sender
from receiver import Receiver
import struct
import time

class Client:
    def __init__(self, listen_port, server_port, server_ip, query, filename):
        self.listen_port = listen_port
        self.server_port = server_port
        self.server_ip = server_ip
        self.query = query
        self.filename = filename

    def run(self):
        if self.query:
            self.query_file()
        else:
            self.send_file()
    
    def send_file(self):
        # create a packet to send to the server that contains  the filename
        encoded_filename = bytes(self.filename, 'utf-8')

        # read file into data variable
        with open(self.filename, 'rb') as f:
            data = f.read()

        # send the packet to the server
        sender = Sender(self.server_ip, self.server_port, self.listen_port, filename)
        sender.send_data()
        # ensure we received an ack from the server
        sender.sock.close()

        sender = Sender(self.server_ip, self.server_port, self.listen_port, data)
        sender.send_data()
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client")
    parser.add_argument("--listen-port", type=int, required=True, help="Client's listening port")
    parser.add_argument("--server-port", type=int, required=True, help="Client's sending port")
    parser.add_argument("--server-ip", type=str, default="127.0.0.1", help="IP address of the server")
    parser.add_argument("-q", "--query", action="store_true", help="Query mode")
    args = parser.parse_args()

    filename = input("Enter the filename: ")
    client = Client(args.listen_port, args.server_port, args.server_ip, args.query, filename)
    client.run()