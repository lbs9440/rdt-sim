import argparse
import time
from client import Client
from server import Server

class Simulator:
    def __init__(self, filename, drop_rate=0, reorder=False, corrupt=False):
        self.filename = filename
        self.client = Client()
        self.server = Server(output_file="output_" + filename)
        self.drop_rate = drop_rate
        self.reorder = reorder
        self.corrupt = corrupt

    def start(self):
        print("[Simulator] Starting server...")
        from threading import Thread
        server_thread = Thread(target=self.server.start, daemon=True)
        server_thread.start()
        
        time.sleep(1)  # Give the server time to start
        print("[Simulator] Starting client...")
        self.client.send_file(self.filename)

    def stop(self):
        self.client.close()
        self.server.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable Data Transfer Simulator")
    parser.add_argument("filename", help="File to transfer")
    args = parser.parse_args()

    sim = Simulator(args.filename)
    sim.start()
