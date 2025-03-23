import socket
import struct
import argparse
import time

# Constants
PACKET_SIZE = 50  # Adjust the size of your packets as needed
BUFFER_SIZE = 2048
TIMEOUT = 15  # Timeout for receiving ACKs (in seconds)
MAX_PAYLOAD_SIZE = PACKET_SIZE - 6  # Reserve 6 bytes for the sequence number and checksum
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

class Sender:
    def __init__(self, receiver_ip, receiver_port, listening_port, data):
        """
        Represents a Go-Back-N sender for reliable data transmission.
        
        :param receiver_ip: IP address of the receiver to send to
        :param receiver_port: Port number of the receiver to send to
        :param listening_port: Port number to listen for ACKs
        :param data: Data to be sent
        
        The object will be initialized with the given parameters and the necessary data structures will be set up
        """
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        if not isinstance(data, bytes):
            self.data = bytes(data, 'utf-8')
        else:
            self.data = data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT) 
        self.sock.bind(("127.0.0.1", listening_port))
        self.seq_num = 0  
        self.window_size = 5  
        self.acks = [False] * self.window_size 
        self.window_start = 0 
        self.eot_sent = False
        self.shutoff = 0

    def send_data(self):
        """Handles the transmission of data packets and manages acknowledgments."""
        print("Sender started.")
        total_packets = (len(self.data) + MAX_PAYLOAD_SIZE - 1) // MAX_PAYLOAD_SIZE
        
        while self.seq_num < total_packets:
            if self.seq_num < self.window_start + self.window_size:
                packet_data = self.data[self.seq_num * MAX_PAYLOAD_SIZE: (self.seq_num + 1) * MAX_PAYLOAD_SIZE]
                self.send_packet(self.seq_num, packet_data)
            
            self.handle_acks()
        
        self.send_packet(END_OF_TRANSMISSION, b"")

        self.eot_sent = True
        self.shutoff = time.time() + 15

        try:
            self.handle_acks()
        except socket.timeout:
            print("No ACK received for EOT packet, ending transmission anyway.")

        print("Data transmission complete.")
    

    def send_packet(self, seq_num, data):
        """Sends a single packet with a sequence number and checksum.
        
        :param seq_num: Sequence number of the packet.
        :param data: Payload data to be sent.
        """
        checksum = calculate_checksum(data)
        packet = struct.pack('!I', seq_num) + struct.pack('!H', checksum) + data
        self.sock.sendto(packet, (self.receiver_ip, self.receiver_port))
        print(f"Sent packet {seq_num}")

    def handle_acks(self):
        """Handles acknowledgment reception and manages the sliding window."""
        while True:
            try:
                if time.time() > self.shutoff and self.eot_sent:
                    self.sock.close()
                    return
                
                ack_data, _ = self.sock.recvfrom(BUFFER_SIZE)
                ack_seq_num, checksum = struct.unpack('!IH', ack_data[:6])
                if checksum != calculate_checksum(bytes("ACK", 'utf-8')):
                    print(f"Received ACK {ack_seq_num} with incorrect checksum, ignoring...")
                    continue

                print(f"Received ACK {ack_seq_num} for packet {ack_seq_num}")

                if self.eot_sent:
                    self.sock.close()
                    return
                
                self.update_window(ack_seq_num)
                break  
            except (socket.timeout, BlockingIOError, IOError):
                self.retransmit_next_packet()

    def retransmit_next_packet(self):
        """Retransmits the next unacknowledged packet in the window."""
        for i in range(self.window_size):
            packet_index = self.window_start + i
            if not self.acks[i]:  
                time.sleep(1)
                packet_data = self.data[packet_index * MAX_PAYLOAD_SIZE: (packet_index + 1) * MAX_PAYLOAD_SIZE]
                self.send_packet(packet_index, packet_data)
                print(f"Retransmitting packet {packet_index}")
                break 


    def update_window(self, ack_seq_num):
        """Shifts the sliding window based on received acknowledgments.
        
        :param ack_seq_num: Sequence number of the received acknowledgment.
        """
        shift = ack_seq_num - self.window_start + 1  
        if shift > 0:
            self.acks = [False] * self.window_size 
            self.window_start += shift  
            self.seq_num = self.window_start 

            # Stop if all packets are acknowledged
            if self.window_start >= len(self.data):
                self.sock.close()
                return

def main():
    """Parses command-line arguments and initializes the sender."""    
    parser = argparse.ArgumentParser(description="UDP Go-Back-N Sender")
    parser.add_argument("--receiver-port", type=int, required=True, help="Receiver's port number")
    parser.add_argument("--receiver-ip", type=str, default="127.0.0.1", help="IP address of the receiver")
    parser.add_argument("--listening-port", type=int, required=True, help="This sender's port number")
    parser.add_argument("--data", type=str, required=True, help="Data to send")

    args = parser.parse_args()

    sender = Sender(args.receiver_ip, args.receiver_port, args.listening_port, args.data)
    sender.send_data()

if __name__ == "__main__":
    main()
