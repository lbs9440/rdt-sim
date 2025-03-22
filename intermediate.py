import socket
import struct
import argparse
import random

# Constants
BUFFER_SIZE = 2048
END_OF_TRANSMISSION = 0xFFFFFF
TIMEOUT_TIME = 10

class Intermediate:
    def __init__(self, listen_port, sender_ip, sender_port, receiver_ip, receiver_port, loss_prob, reorder_prob, corrupt_prob):
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.loss_prob = loss_prob
        self.reorder_prob = reorder_prob
        self.corrupt_prob = corrupt_prob
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", listen_port))  # Listen on receiver's port
        self.sock.settimeout(TIMEOUT_TIME)
        self.socket_closed = False
        self.packet_buffer = []

    def start(self):
        print("Intermediate started.")
        while True:
            # Check for packets from sender
            self.handlePackets()
            if self.socket_closed:
                print("Socket closed. Timeout in {TIMEOUT_TIME} seconds after not sending/receiving any packets...")
                break
            
    def handlePackets(self):
        try:
            packet, addr = self.sock.recvfrom(BUFFER_SIZE)
            if addr[1] == self.sender_port:
                self.handle_data_packet(packet)
            else:
                self.handle_ack_packet(packet)
        except socket.timeout:
            self.sock.close()
            self.socket_closed = True
    
    def handle_data_packet(self, packet):
        """Handles data packets from sender and forwards them to receiver."""
        if random.random() < self.loss_prob:
            print("Data packet lost (simulated).")
            return
        if random.random() < self.corrupt_prob:
            print("Data packet corrupted (simulated).")
            packet = self.corrupt_packet(packet)
        if random.random() < self.reorder_prob:
            print("Data packet reordered (simulated).")
            self.packet_buffer.append(packet)
            if len(self.packet_buffer) > 1:
                # Swap last two packets
                self.packet_buffer[-1], self.packet_buffer[-2] = self.packet_buffer[-2], self.packet_buffer[-1]
            for pkt in self.packet_buffer:
                self.sock.sendto(pkt, (self.receiver_ip, self.receiver_port))
            self.packet_buffer.clear()
        else:
            self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))

    def handle_ack_packet(self, packet):
        """Handles ACK packets from receiver and forwards them to sender."""
        if random.random() < self.loss_prob:
            print("ACK lost (simulated).")
            return
        if random.random() < self.corrupt_prob:
            print("ACK corrupted (simulated).")
            packet = self.corrupt_packet(packet)
        self.sock.sendto(packet, (self.sender_ip, self.sender_port))

    def corrupt_packet(self, packet):
        """Corrupt a packet by flipping some bits."""
        packet = bytearray(packet)
        for i in range(len(packet)):
            if random.random() < 0.1:  # 10% chance to flip each byte
                packet[i] ^= 0xFF  # Flip all bits in the byte
        return bytes(packet)


def main():
    parser = argparse.ArgumentParser(description="UDP Intermediate Simulator")
    parser.add_argument("--sender-port", type=int, required=True, help="Sender's port number")
    parser.add_argument("--receiver-port", type=int, required=True, help="Receiver's port number")
    parser.add_argument("--listen-port", type=int, required=True, help="This intermediate's port number")
    parser.add_argument("--loss", action="store_true", help="Enable packet loss simulation")
    parser.add_argument("--reorder", action="store_true", help="Enable packet reordering simulation")
    parser.add_argument("--corrupt", action="store_true", help="Enable packet corruption simulation")

    args = parser.parse_args()

    # Set probabilities for each type of network impairment
    loss_prob = 0.1 if args.loss else 0.0
    reorder_prob = 0.1 if args.reorder else 0.0
    corrupt_prob = 0.1 if args.corrupt else 0.0

    intermediate = Intermediate(args.listen_port, "127.0.0.1", args.sender_port, "127.0.0.1", args.receiver_port, loss_prob, reorder_prob, corrupt_prob)
    intermediate.start()

if __name__ == "__main__":
    main()