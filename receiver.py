import socket
import struct
import argparse
import time

# Constants
BUFFER_SIZE = 2048
END_OF_TRANSMISSION = 0xFFFFFF  # Define EOT constant here
SOCKET_TIMEOUT = 10

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
    """Go-Back-N Receiver.

    This class listens for incoming packets, verifies their integrity using checksums, 
    acknowledges received packets, and handles packet loss and reordering.
    """
    def __init__(self, listen_port, receiver_ip):
        """Initialize the receiver.

        :param listen_port: Port number to listen on.
        :param receiver_ip: IP address of the receiver.
        """
        self.listen_port = listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((receiver_ip, listen_port))
        self.sock.settimeout(2)
        self.expected_seq_num = 0
        self.received_data = {}
        self.sender_address = None
        self.shutoff = -1

    def start_receiving(self):
        """Listen for incoming packets, validate checksums, and send acknowledgments.

        This method continuously listens for packets, processes them in sequence,
        and acknowledges correctly received packets. It also handles out-of-order 
        packets and retransmission scenarios.
        """
        print(f"Receiver listening on port {self.listen_port}...")

        while True:
            try:
                packet, sender_address = self.sock.recvfrom(BUFFER_SIZE)
                if time.time() > self.shutoff and self.shutoff != -1:
                    print(f"No proper packet received for {SOCKET_TIMEOUT} seconds, ending transmission...")
                    self.sock.close()
                    return
                self.sender_address = sender_address
                seq_num, checksum = struct.unpack('!IH', packet[:6])

                if calculate_checksum(packet[6:]) != checksum:
                    print(f"Received packet {seq_num} with incorrect checksum, ignoring...")
                    continue

                checksum = calculate_checksum(packet[6:])
                
                if seq_num == END_OF_TRANSMISSION:
                    print("Received last packet, sending final ACK...")
                    checksum = calculate_checksum("ACK".encode())
                    self.sock.sendto(struct.pack('!I', END_OF_TRANSMISSION) + struct.pack('!H', checksum), sender_address)
                    self.sock.close()
                    break

                if seq_num == self.expected_seq_num:
                    print(f"Received packet {seq_num}, sending ACK...")
                    checksum = calculate_checksum("ACK".encode())
                    self.sock.sendto(struct.pack('!I', seq_num) + struct.pack('!H', checksum), sender_address)
                    self.expected_seq_num += 1
                    self.received_data[seq_num] = packet[6:] 
                    self.shutoff = time.time() + SOCKET_TIMEOUT

                elif seq_num > self.expected_seq_num:
                    print(f"Received out-of-order packet {seq_num}, expected {self.expected_seq_num}")
                    self.received_data[seq_num] = packet[6:]
                
                elif seq_num < self.expected_seq_num:
                    print(f"Received out-of-order packet {seq_num}, expected {self.expected_seq_num}, resending {seq_num}")
                    checksum = calculate_checksum("ACK".encode())
                    self.sock.sendto(struct.pack('!I', seq_num) + struct.pack('!H', checksum), sender_address)

            except socket.timeout:
                pass

    def reassemble_data(self):
        """Reassemble received packets into a complete data sequence for files.

        :return: The complete data reconstructed from received packets.
        """
        complete_data = b''
        for i in range(0, len(self.received_data)):
            complete_data += self.received_data[i]
        return complete_data 
    
    def return_filename(self):
        """Retrieve the filename from the received data.

        :return: The filename extracted from the first received packet.
        """
        print(self.received_data[0].decode('utf-8'))
        return self.received_data[0].decode('utf-8')


def main():
    """Parse command-line arguments and start the receiver."""
    parser = argparse.ArgumentParser(description="UDP Go-Back-N Receiver")
    parser.add_argument("--listen-port", type=int, required=True, help="Port to listen on")
    parser.add_argument("--receiver-ip", type=str, default="127.0.0.1", help="IP address of the receiver")
    
    args = parser.parse_args()

    receiver = Receiver(args.listen_port, args.receiver_ip)
    receiver.start_receiving()

if __name__ == "__main__":
    main()
