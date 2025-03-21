import socket
import struct
import argparse
import time

# Constants
PACKET_SIZE = 52  # Adjust the size of your packets as needed
BUFFER_SIZE = 2048
TIMEOUT = 2  # Timeout for receiving ACKs (in seconds)
MAX_PAYLOAD_SIZE = PACKET_SIZE - 4  # Reserve 4 bytes for the sequence number
END_OF_TRANSMISSION = 0xFFFFFF  # Define EOT constant here

class Sender:
    def __init__(self, receiver_ip, receiver_port, data):
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.data = data.encode()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)  # Set timeout for receiving ACKs
        self.seq_num = 0  # Sequence number for the first packet
        self.window_size = 5  # The size of the sliding window
        self.acks = [False] * self.window_size  # List to track which packets have been acknowledged
        self.window_start = 0  # Start of the current window

    def send_data(self):
        print("Sender started.")
        total_packets = (len(self.data) + MAX_PAYLOAD_SIZE - 1) // MAX_PAYLOAD_SIZE  # Total number of packets
        
        while self.seq_num < total_packets:
            # If the sequence number is within the window, send it
            if self.seq_num < self.window_start + self.window_size:
                packet_data = self.data[self.seq_num * MAX_PAYLOAD_SIZE: (self.seq_num + 1) * MAX_PAYLOAD_SIZE]
                self.send_packet(self.seq_num, packet_data)
            
            # Wait for ACKs and shift the window
            self.handle_acks()
        
        # Send the End-of-Transmission (EOT) packet after sending all data packets
        self.send_packet(END_OF_TRANSMISSION, b"")
        print("Sent End-of-Transmission (EOT) packet.")

        # Wait for final ACK of EOT packet
        self.handle_acks()

        print("Data transmission complete.")

    def send_packet(self, seq_num, data):
        """Send a single packet."""
        packet = struct.pack('!I', seq_num) + data
        self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))
        print(f"Sent packet {seq_num}")

    def handle_acks(self):
        """Wait for ACKs and shift the window accordingly."""
        while True:
            try:
                ack_data, _ = self.sock.recvfrom(BUFFER_SIZE)
                ack_seq_num = struct.unpack('!I', ack_data[:4])[0]
                print(f"Received ACK {ack_seq_num} for packet {ack_seq_num}")
                
                # Update the acknowledgment list and shift window
                self.update_window(ack_seq_num)
                break  # Exit after receiving a valid ACK
            except (socket.timeout, BlockingIOError, IOError):
                # If there's a timeout or I/O error, retransmit the next unacknowledged packet
                self.retransmit_next_packet()

    def retransmit_next_packet(self):
        """Retransmit the next unacknowledged packet."""
        for i in range(self.window_size):
            packet_index = self.window_start + i
            if not self.acks[i]:  # If the packet at this index hasn't been acknowledged
                # Send the packet
                time.sleep(2)
                packet_data = self.data[packet_index * MAX_PAYLOAD_SIZE: (packet_index + 1) * MAX_PAYLOAD_SIZE]
                self.send_packet(packet_index, packet_data)
                print(f"Retransmitting packet {packet_index}")
                break  # Retransmit only the next unacknowledged packet


    def update_window(self, ack_seq_num):
        """Shift the window based on the received ACK."""
        shift = ack_seq_num - self.window_start + 1  # How much to shift the window based on the latest ACK
        if shift > 0:
            # Update the acknowledgment list
            self.acks = [False] * self.window_size  # Reset ACK list for the new window
            self.window_start += shift  # Move the start of the window forward
            self.seq_num = self.window_start  # Set the new sequence number

            # Stop if all packets are acknowledged
            if self.window_start >= len(self.data):
                self.sock.close()
                return

def main():
    # Set up argument parsing for receiver IP, port, and data
    parser = argparse.ArgumentParser(description="UDP Go-Back-N Sender")
    parser.add_argument("--receiver-ip", type=str, required=True, help="Receiver's IP address")
    parser.add_argument("--receiver-port", type=int, required=True, help="Receiver's port number")
    parser.add_argument("--data", type=str, required=True, help="Data to send")

    args = parser.parse_args()

    # Create a Sender object and start sending data
    sender = Sender(args.receiver_ip, args.receiver_port, args.data)
    sender.send_data()

if __name__ == "__main__":
    main()
