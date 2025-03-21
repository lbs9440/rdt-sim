import socket
import struct

# Constants
PACKET_SIZE = 52  # Max data per packet
BUFFER_SIZE = 2048  # Buffer size for ACK reception
END_OF_TRANSMISSION = 0xFFFFFF  # Special sequence number for last packet

class Receiver:
    def __init__(self, listen_port):
        self.listen_port = listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", listen_port))
        self.sock.settimeout(5)  # Set timeout to avoid indefinite blocking
        self.expected_seq_num = 0  # Expecting 0th packet initially
        self.received_data = {}  # To store received data chunks

    def start_receiving(self):
        """Listens for packets and sends ACKs."""
        print(f"Receiver listening on port {self.listen_port}...")

        while True:
            try:
                packet, sender_address = self.sock.recvfrom(BUFFER_SIZE)
                seq_num = struct.unpack('!I', packet[:4])[0]  # Extract sequence number

                if seq_num == self.expected_seq_num:
                    print(f"Received packet {seq_num}, sending ACK...")
                    self.sock.sendto(struct.pack('!I', seq_num), sender_address)
                    self.expected_seq_num += 1

                    # Store the data chunk for reassembly later
                    self.received_data[seq_num] = packet[4:]

                # Check if it's the last packet
                elif seq_num == END_OF_TRANSMISSION:
                    print("Received last packet, sending final ACK...")
                    self.sock.sendto(struct.pack('!I', END_OF_TRANSMISSION), sender_address)
                    self.reassemble_data()
                    self.sock.close()
                    break
                        
            except socket.timeout:
                pass  # Timeout if no data received

    def reassemble_data(self):
        """Reassembles data once all packets are received."""
        # Sort the received packets by sequence number and concatenate them
        sorted_data = [self.received_data[i] for i in sorted(self.received_data.keys())]
        complete_data = b''.join(sorted_data)

        print("Reassembled data: ", complete_data.decode())
        self.sock.close()
