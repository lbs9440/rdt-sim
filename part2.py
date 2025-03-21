# simulator.py
import argparse
import threading
from sender import Sender
from receiver import Receiver

def main():
    """Parses arguments and starts sender/receiver threads."""
    parser = argparse.ArgumentParser(description="UDP Go-Back-N Simulator")
    parser.add_argument("--receiver-port", type=int, required=True, help="Port for receiver to listen on")
    parser.add_argument("--sender-ip", type=str, required=True, help="Receiver IP address for sending data")
    parser.add_argument("--sender-port", type=int, required=True, help="Receiver port for sending data")
    parser.add_argument("--data", type=str, required=True, help="Data to send")
    parser.add_argument("--loss", action="store_true", help="Enable packet loss simulation")
    parser.add_argument("--reorder", action="store_true", help="Enable packet reordering simulation")
    parser.add_argument("--corrupt", action="store_true", help="Enable packet corruption simulation")
    
    args = parser.parse_args()

    # Start receiver thread
    receiver = Receiver(args.receiver_port)
    receiver_thread = threading.Thread(target=receiver.start_receiving, daemon=True)
    receiver_thread.start()

    # Start sender thread
    sender = Sender(args.sender_ip, args.sender_port, args.data)
    sender_thread = threading.Thread(target=sender.send_data)
    sender_thread.start()

    sender_thread.join()  # Wait for sender to finish before exiting

if __name__ == "__main__":
    main()
