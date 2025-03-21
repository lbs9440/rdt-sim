import socket
import struct
import hashlib

class Server:
    def __init__(self, host="0.0.0.0", port=5000, output_file="received.txt"):
        self.host = host
        self.port = port
        self.output_file = output_file
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.expected_seq = 0

    def calculate_checksum(self, data):
        return hashlib.md5(data).hexdigest().encode()

    def start(self):
        print("[Server] Listening for incoming packets...")
        with open(self.output_file, "wb") as f:
            while True:
                packet, addr = self.sock.recvfrom(1024)
                seq_num, checksum = struct.unpack("I32s", packet[:36])
                data = packet[36:]

                if self.calculate_checksum(data) == checksum:
                    print(f"[Server] Received packet {seq_num} (Valid)")
                    if seq_num == self.expected_seq:
                        f.write(data)
                        self.expected_seq += 1

                ack = struct.pack("I", seq_num)
                self.sock.sendto(ack, addr)
                print(f"[Server] Sent ACK {seq_num}")

    def close(self):
        self.sock.close()
