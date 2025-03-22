import socket
import struct
import argparse

# Constants
BUFFER_SIZE = 2048
END_OF_TRANSMISSION = 0xFFFFFF  # Define EOT constant here

def calculate_checksum(data):
    """Compute the checksum of the given data
    
    :param data: data to compute the checksum
    :return checksum:
    """
    if len(data) % 2:
        data += b'\x00' 
    checksum = sum((data[i] << 8) + data[i + 1] for i in range(0, len(data), 2))
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum = ~checksum & 0xFFFF
    return checksum

class Receiver:
    def __init__(self, listen_port):
        self.listen_port = listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", listen_port))
        self.sock.settimeout(5)
        self.expected_seq_num = 0
        self.received_data = {}

    def start_receiving(self):
        """Listen for incoming packets and send ACKs."""
        print(f"Receiver listening on port {self.listen_port}...")

        while True:
            try:
                packet, sender_address = self.sock.recvfrom(BUFFER_SIZE)
                seq_num, checksum = struct.unpack('!IH', packet[:6])

                if calculate_checksum(packet[6:]) != checksum:
                    print(f"Received packet {seq_num} with incorrect checksum, ignoring...")
                    continue

                checksum = calculate_checksum(packet[6:])
                
                if seq_num == END_OF_TRANSMISSION:
                    # End of transmission, acknowledge the last packet and reassemble data
                    print("Received last packet, sending final ACK...")
                    checksum = calculate_checksum("ACK".encode())
                    self.sock.sendto(struct.pack('!I', END_OF_TRANSMISSION) + struct.pack('!H', checksum), sender_address)
                    self.reassemble_data()
                    self.sock.close()  # Close the socket after transmission is complete
                    break

                if seq_num == self.expected_seq_num:
                    # Correct sequence number, store the data and send ACK
                    print(f"Received packet {seq_num}, sending ACK...")
                    checksum = calculate_checksum("ACK".encode())
                    self.sock.sendto(struct.pack('!I', seq_num) + struct.pack('!H', checksum), sender_address)
                    self.expected_seq_num += 1  # Expect the next sequence number
                    self.received_data[seq_num] = packet[6:]  # Store the data part of the packet

                elif seq_num > self.expected_seq_num:
                    # Out-of-order packet, store for later
                    print(f"Received out-of-order packet {seq_num}, expected {self.expected_seq_num}")
                    self.received_data[seq_num] = packet[6:]
                
                # elif an ack packet was lost, resend ack packet of data packet being sent
                elif seq_num < self.expected_seq_num:
                    print(f"Received out-of-order packet {seq_num}, expected {self.expected_seq_num}, resending {seq_num}")
                    checksum = calculate_checksum("ACK".encode())
                    self.sock.sendto(struct.pack('!I', seq_num) + struct.pack('!H', checksum), sender_address)

                

            except socket.timeout:
                pass  # Ignore timeouts, keep listening for packets

    def reassemble_data(self):
        """Reassemble and print complete data."""
        # Sort received data by sequence number
        sorted_data = [self.received_data[i] for i in sorted(self.received_data.keys())]
        complete_data = b''.join(sorted_data)  # Concatenate all the data parts
        print("Reassembled data: ", complete_data.decode())  # Print the complete data as a string

def main():
    parser = argparse.ArgumentParser(description="UDP Go-Back-N Receiver")
    parser.add_argument("--listen-port", type=int, required=True, help="Port to listen on")
    
    args = parser.parse_args()

    receiver = Receiver(args.listen_port)
    receiver.start_receiving()

if __name__ == "__main__":
    main()
