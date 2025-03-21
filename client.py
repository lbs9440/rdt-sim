import socket
import struct
import time
import hashlib

class Client:
    def __init__(self, server_ip="127.0.0.1", server_port=5000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)  # Set timeout for ACKs

    def calculate_checksum(self, data):
        return hashlib.md5(data).hexdigest().encode()


    def send_file(self, filename):
        with open(filename, "rb") as f:
            seq_num = 0
            window = {}

            while True:
                while len(window) < 4:
                    chunk = f.read(1016)  # Reserve space for header
                    if not chunk:
                        break  # EOF

                    checksum = self.calculate_checksum(chunk)
                    packet = struct.pack("I32s", seq_num, checksum) + chunk
                    self.sock.sendto(packet, (self.server_ip, self.server_port))
                    window[seq_num] = (packet, time.time())
                    print(f"[Client] Sent packet {seq_num}")

                    seq_num += 1
                
                try:
                    ack, _ = self.sock.recvfrom(4)
                    ack_num = struct.unpack("I", ack)[0]
                    print(f"[Client] Received ACK {ack_num}")
                    if ack_num in window:
                        del window[ack_num]

                except socket.timeout:
                    print("[Client] Timeout! Retransmitting...")
                    for seq in list(window.keys()):
                        self.sock.sendto(window[seq][0], (self.server_ip, self.server_port))

    def close(self):
        self.sock.close()