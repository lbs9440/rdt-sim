import socket
import struct
import argparse
import random

# Constants
BUFFER_SIZE = 2048
END_OF_TRANSMISSION = 0xFFFFFF
TIMEOUT_TIME = 20

class Intermediate:
    """
    An intermediate node that simulates network impairments such as
    packet loss, reordering, and corruption between a sender and a receiver.
    """
    def __init__(self, listen_port, sender_ip, sender_port, receiver_ip, receiver_port, loss_prob, reorder_prob, corrupt_prob):
        """
        Initializes the Intermediate node with specified network parameters.

        :param listen_port: Port number to listen on for incoming packets.
        :param sender_ip: IP address of the sender.
        :param sender_port: Port number of the sender.
        :param receiver_ip: IP address of the receiver.
        :param receiver_port: Port number of the receiver.
        :param loss_prob: If loss prob will be active.
        :param reorder_prob: If reorder prob will be active.
        :param corrupt_prob: If corrupt prob will be active.
        """
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
        """
        Starts the intermediate node, continuously handling packets until terminated.
        """
        print("Intermediate started.")
        while True:
            # Check for packets from sender
            self.handlePackets()
            if self.socket_closed:
                print(f"Socket closed. Exiting...")
                break
            
    def handlePackets(self):
        """
        Handles incoming packets, distinguishing between data and ACK packets.
        """
        try:
            packet, addr = self.sock.recvfrom(BUFFER_SIZE)
            if addr[1] == self.sender_port:
                self.handle_data_packet(packet)
            else:
                self.handle_ack_packet(packet)
        except (socket.timeout, ConnectionResetError):
            self.sock.close()
            self.socket_closed = True
    
    def handle_data_packet(self, packet):
        """
        Handles incoming data packets, simulating packet loss, corruption, and reordering as specified.

        :param packet: The incoming data packet.
        """
        original_packet = packet
        if random.random() < self.loss_prob:
            print("\nData packet lost (simulated).")
            print(f"Contents of dropped packet: {original_packet}\n")
            return
        if random.random() < self.corrupt_prob:
            print("\nData packet corrupted (simulated).")
            packet = self.corrupt_packet(packet)
            print(f"Original packet: {original_packet}")
            print(f"Corrupted packet: {packet}")
            print(f"Difference: {bytes([a ^ b for a, b in zip(original_packet, packet)])}\n")
        if random.random() < self.reorder_prob:
            print("\nData packet reordered (simulated).")
            self.packet_buffer.append(packet)
            if len(self.packet_buffer) > 1:
                # Swap last two packets
                print(f"Original packet buffer: {self.packet_buffer}")
                self.packet_buffer[-1], self.packet_buffer[-2] = self.packet_buffer[-2], self.packet_buffer[-1]
                print(f"Reordered packet buffer: {self.packet_buffer}\n")
            for pkt in self.packet_buffer:
                self.sock.sendto(pkt, (self.receiver_ip, self.receiver_port))
            self.packet_buffer.clear()
        else:
            self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))

    def handle_ack_packet(self, packet):
        """
        Handles incoming ACK packets, simulating packet loss and corruption as specified.

        :param packet: The incoming ACK packet.
        """
        original_packet = packet
        if random.random() < self.loss_prob:
            print("\nACK lost (simulated).")
            print(f"Contents of dropped packet: {packet}\n")
            return
        if random.random() < self.corrupt_prob:
            print("\nACK corrupted (simulated).")
            packet = self.corrupt_packet(packet)
            print(f"Original packet: {original_packet}")
            print(f"Corrupted packet: {packet}")
            print(f"Difference: {bytes([a ^ b for a, b in zip(original_packet, packet)])}\n")
        self.sock.sendto(packet, (self.sender_ip, self.sender_port))

    def corrupt_packet(self, packet):
        """Corrupts a packet by randomly flipping bits in it.

        :param packet: The packet to corrupt.
        :return: The corrupted packet.
        """
        packet = bytearray(packet)
        for i in range(len(packet)):
            if random.random() < 0.1: 
                packet[i] ^= 0xFF 
        return bytes(packet)


def main():
    """
    Parses command-line arguments and starts the intermediate node.
    """
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