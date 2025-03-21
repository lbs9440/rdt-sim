import socket
import random
import time
import struct

BUFFER_SIZE = 2048
PACKET_LOSS_RATE = 0.1
REORDER_RATE = 0.1
DELAY_RATE = 0.2

class Intermediate:
    def __init__(self, listen_address, receiver_address):
        self.listen_address = listen_address
        self.receiver_address = receiver_address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.listen_address)

    def process_packets(self):
        print("Intermediate server running...")
        while True:
            packet, sender_address = self.sock.recvfrom(BUFFER_SIZE)
            seq_num = struct.unpack('!I', packet[:4])[0]

            if random.random() < PACKET_LOSS_RATE:
                print(f"Packet {seq_num} lost!")
                continue

            if random.random() < REORDER_RATE:
                time.sleep(0.5)
                print(f"Packet {seq_num} delayed!")

            self.sock.sendto(packet, self.receiver_address)

if __name__ == "__main__":
    intermediate = Intermediate(("127.0.0.1", 12345), ("127.0.0.1", 12346))
    intermediate.process_packets()
