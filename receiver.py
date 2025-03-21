import socket
import struct
import argparse

# Constants
BUFFER_SIZE = 2048
END_OF_TRANSMISSION = 0xFFFFFF  # Define EOT constant here

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
                seq_num = struct.unpack('!I', packet[:4])[0]
                
                if seq_num == END_OF_TRANSMISSION:
                    # End of transmission, acknowledge the last packet and reassemble data
                    print("Received last packet, sending final ACK...")
                    self.sock.sendto(struct.pack('!I', END_OF_TRANSMISSION), sender_address)
                    self.reassemble_data()
                    self.sock.close()  # Close the socket after transmission is complete
                    break

                if seq_num == self.expected_seq_num:
                    # Correct sequence number, store the data and send ACK
                    print(f"Received packet {seq_num}, sending ACK...")
                    self.sock.sendto(struct.pack('!I', seq_num), sender_address)
                    self.expected_seq_num += 1  # Expect the next sequence number
                    self.received_data[seq_num] = packet[4:]  # Store the data part of the packet

                elif seq_num > self.expected_seq_num:
                    # Out-of-order packet, store for later
                    print(f"Received out-of-order packet {seq_num}, expected {self.expected_seq_num}")
                    self.received_data[seq_num] = packet[4:]

                

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
