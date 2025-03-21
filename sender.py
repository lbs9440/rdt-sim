import socket
import struct
import threading
import time

# Constants
PACKET_SIZE = 52  # Max data per packet
WINDOW_SIZE = 5   # Go-Back-N window size
TIMEOUT = 2       # Retransmission timeout
BUFFER_SIZE = 2048  # Buffer size for ACK reception
END_OF_TRANSMISSION = 0xFFFFFF  # Special sequence number for last packet

class Sender:
    def __init__(self, receiver_ip, receiver_port, data):
        self.receiver_address = (receiver_ip, receiver_port)
        self.data = data.encode()  # Convert string data to bytes
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)  # Set socket timeout
        self.sequence_number = 0  # Start at 0
        self.window_start = 0
        self.acks_received = [False] * WINDOW_SIZE
        self.packets = self.chunk_data()
        self.lock = threading.Lock()
        self.final_ack_received = False  # Flag to track if final ACK is received

    def chunk_data(self):
        """Splits data into fixed-size packets."""
        return [self.data[i:i+PACKET_SIZE] for i in range(0, len(self.data), PACKET_SIZE)]

    def create_packet(self, seq_num, data_chunk):
        """Creates a packet with sequence number + data."""
        return struct.pack('!I', seq_num) + data_chunk

    def send_packet(self, seq_num):
        """Sends a single packet."""
        if seq_num < len(self.packets):
            packet = self.create_packet(seq_num, self.packets[seq_num])
            self.sock.sendto(packet, self.receiver_address)
            print(f"Sent packet {seq_num}")
        elif seq_num == len(self.packets):  # Send the last packet
            packet = self.create_packet(END_OF_TRANSMISSION, b"")  # Send empty data for last packet
            self.sock.sendto(packet, self.receiver_address)
            print(f"Sent last packet {END_OF_TRANSMISSION}")

    def handle_acks(self):
        """Listens for ACKs and moves the sliding window."""
        while not self.final_ack_received and self.window_start < len(self.packets) + 1:  # Include last packet in window
            try:
                ack_data, _ = self.sock.recvfrom(BUFFER_SIZE)
                ack_num = struct.unpack('!I', ack_data)[0]
                print(f"Received ACK {ack_num}")

                # If we received an ACK for END_OF_TRANSMISSION, we stop the transmission
                if ack_num == END_OF_TRANSMISSION:
                    print("Received final ACK for END_OF_TRANSMISSION.")
                    self.final_ack_received = True  # Mark final ACK as received
                    break

                if ack_num >= self.window_start:
                    with self.lock:
                        self.acks_received[ack_num % WINDOW_SIZE] = True

                    while self.acks_received[self.window_start % WINDOW_SIZE]:
                        with self.lock:
                            self.acks_received[self.window_start % WINDOW_SIZE] = False
                            self.window_start += 1
            except socket.timeout:
                self.retransmit_packets()

    def retransmit_packets(self):
        """Retransmits packets in case of timeout."""
        if not self.final_ack_received:
            print("Timeout! Retransmitting window...")
            with self.lock:
                for i in range(self.window_start, min(self.window_start + WINDOW_SIZE, len(self.packets))):
                    print(f"Retransmitting packet {i}")
                    self.send_packet(i)

    # Start the thread without setting it as a daemon thread
    def send_data(self):
        ack_thread = threading.Thread(target=self.handle_acks)  # Create the thread without daemon=True
        ack_thread.start()

        while self.window_start < len(self.packets):  # Send all packets except the last one
            # Send packets within the window
            for i in range(self.window_start, min(self.window_start + WINDOW_SIZE, len(self.packets))):
                self.send_packet(i)

            # Wait for ACKs, then shift the window
            time.sleep(0.5)

        # Send the last packet once after all others are acknowledged
        self.send_packet(len(self.packets))  # Send the last packet (END_OF_TRANSMISSION)

        # Wait for the ACK for END_OF_TRANSMISSION
        self.handle_acks()

        # Ensure the thread finishes before closing the socket
        ack_thread.join()  # Wait for the ack_thread to finish

        # Close the socket once all packets are sent and END_OF_TRANSMISSION ACK is received
        print("Transmission complete.")
        self.sock.close()

