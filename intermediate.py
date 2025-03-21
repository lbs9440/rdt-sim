import socket
import random
import time

class Intermediate:
    def __init__(self, sender_ip, sender_port, receiver_port, loss=False, reorder=False, corrupt=False):
        self.sender_address = (sender_ip, sender_port)
        self.receiver_address = ('127.0.0.1', receiver_port)
        self.loss = loss
        self.reorder = reorder
        self.corrupt = corrupt
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', receiver_port))  # Bind to a local port

    def introduce_loss(self, packet):
        """Simulate packet loss based on probability."""
        if self.loss and random.random() < 0.1:  # 10% packet loss
            print("Packet lost")
            return False
        return True

    def introduce_reordering(self, packets):
        """Simulate packet reordering."""
        if self.reorder and random.random() < 0.1:  # 10% chance to reorder
            random.shuffle(packets)
            print("Packets reordered")
        return packets

    def introduce_corruption(self, packet):
        """Simulate packet corruption."""
        if self.corrupt and random.random() < 0.1:  # 10% chance to corrupt
            corrupted_packet = bytearray(packet)
            corrupted_packet[random.randint(0, len(corrupted_packet) - 1)] ^= random.randint(1, 255)  # Random bit flip
            print("Packet corrupted")
            return bytes(corrupted_packet)
        return packet

    def forward_packets(self):
        """Receives packets from sender and forwards to receiver (and vice versa)."""
        while True:
            try:
                packet, addr = self.sock.recvfrom(2048)
                if addr == self.sender_address:
                    # Packet from sender, forward to receiver
                    if not self.introduce_loss(packet):
                        continue
                    packet = self.introduce_corruption(packet)
                    self.sock.sendto(packet, self.receiver_address)
                    print(f"Forwarded packet to receiver: {packet[:4]}")

                elif addr == self.receiver_address:
                    # Packet from receiver (ACK), forward to sender
                    if not self.introduce_loss(packet):
                        continue
                    packet = self.introduce_corruption(packet)
                    self.sock.sendto(packet, self.sender_address)
                    print(f"Forwarded ACK to sender: {packet[:4]}")

            except Exception as e:
                print(f"Error while forwarding packet: {e}")
                time.sleep(1)  # Allow some delay before retrying
