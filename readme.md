# Reliable File Transfer System

A robust implementation of a reliable file transfer system over UDP using the Go-Back-N protocol, featuring intermediary network simulation for realistic testing.

## Overview

This project implements a client-server architecture for reliable file transfer (RTP) over an unreliable network (UDP). The system employs the Go-Back-N protocol to handle packet loss, corruption, and reordering, making it strong in challenging network conditions. An intermediate node is included to simulate various network 'mess ups' for testing purposes.

## Components

- **Client**: Initiates file transfers to the server or requests files from the server
- **Server**: Receives files from clients and responds to file queries
- **Intermediate Node**: Simulates network impairments between sender and receiver
- **Sender**: Handles the reliable transmission of data using Go-Back-N protocol
- **Receiver**: Processes incoming packets and sends acknowledgments

## Features

- **Reliable Data Transfer**: Ensures data integrity over unreliable UDP connections
- **Go-Back-N Protocol**: Implements sliding window mechanism for efficient retransmission
- **Checksum Verification**: Validates packet integrity to detect corrupted data
- **Network Simulation**: Configurable packet loss, reordering, and corruption rates
- **Bidirectional Transfer**: Supports both uploading and downloading files
- **Timeout Handling**: Automatically retransmits packets when acknowledgments aren't received

## Requirements

- Python 3.6+
- Standard Python libraries (socket, struct, argparse, time, random)

## Project Structure

```
.
├── client.py         # Client implementation for sending/requesting files
├── server.py         # Server implementation for handling file operations
├── sender.py         # Go-Back-N sender implementation
├── receiver.py       # Go-Back-N receiver implementation
├── intermediate.py   # Network simulator for testing
├── Client_files/     # Directory for client's downloaded files
└── Server_files/     # Directory for server's received files
```

## Usage

### Setting Up

Before running the system, ensure you have created the necessary directories:

```bash
mkdir -p Client_files Server_files
```

### Running Network Simulation Without Intermediate Node
Similate sending data packets from a sender to a receiver, and receiving ACK packets back from the receiver

Sender Receiver can be ran in any order, run in separate terminals
```bash
# reveiver-port: what port to send the packets to given the ip
# receiver-ip (optional): what ip to send packets to (defaults to 127.0.0.1 localhost)
# listening-port: sender's port to receiver ACK packets
# data: the data to send to the server
python sender.py --receiver-port 12346 --receiver-ip 127.0.0.1 --listening-port 12345 --data "The data you want to send this data will take more than one packet to transmit all of the data"

# listen-port: receiver's port to receive data packets
# receiver-ip (optional): ip of the receiver itself (defaults to 127.0.0.1 localhost)
python receiver.py --listen-port 12346 --receiver-ip 127.0.0.1
```
### Running Network Simulation With Intermediate Node
To simulate a realistic network environment with packet loss, reordering, and corruption

Each should be ran in a separate terminal in any order, though it is recommended to start the intermediate last as it will time out after not receiving packets for the given TIMEOUT

The flags --loss, --corrupt, and --reorder are all optional flags and if used will set the respective 'mess up' setting to on.

```bash
# In this case no ip is given so it defaults to localhost
# The listening port is the port to receive data packets
python receiver.py --listen-port 12347

# The sender is ran, the reciver port being the listen-port of the intermediate, and the listening-port being its own port where the ACKs are sent to
# Data is the data to send
python sender.py --receiver-port 12346 --listening-port 12345 --data "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam commodo nibh eget bibendum venenatis. Aliquam congue tincidunt mi non consectetur. Morbi purus tellus, pulvinar sit amet elementum in, aliquam vitae risus. Duis facilisis at orci vel lobortis."

# sender-port: where to forward the ACK packets to
# receiver-port: where to forward the data packets to
# listen-port: port of the intermediate node on where to be sent data or ACK packets
# --loss, --corrupt, --reorder (optional): types of 'mess ups' to simulate
python intermediate.py --sender-port 12345 --receiver-port 12347 --listen-port 12346 --loss --corrupt --reorder
```
## Sending Files
### Running the Server

```bash
# server-port: port of the server
# server-ip (optional): IP of the server, defaults to localhost (127.0.0.1)
python server.py --server-port 12500 --server-ip 127.0.0.1
```

### Running the Client

To send a file to the server **(ensure file is in current directory)** Once the client is running, the user is prompted to input a file name:

```bash
# listen-port: port of the client, swaps between sender and receiver based on current task
# server-port: port to send data/files to of the server, also swaps between sender and receiver
# server-ip: ip of the server (optional): defaults to localhost
python client.py --listen-port 12345 --server-port 12500 --server-ip 127.0.0.1
```

To request a file from the server **(ensure the file exists in the Server_files directory)**:

```bash
# -q or --query: flag to let server now to send, rather than receive
python client.py --listen-port 12345 --server-port 12500 -q
```

### Running the Server and Client through an Intermediate Node
Run all in separate terminals, the order doesn't matter, but try to avoid starting intermediate first to avoid timing it out
```bash
python client.py --listen-port 12345 --server-port 12500

python server.py --server-port 12000

python intermediate.py --sender-port 12345 --receiver-port 12000 --listen-port 12500
```
## Protocol Details

### Packet Structure

Each packet consists of:
- 4 bytes: Sequence Number
- 2 bytes: Checksum
- Up to 44 bytes: Payload Data

### Go-Back-N Implementation

- The sender maintains a sliding window of unacknowledged packets
- Packets are sent consecutively up to the window size
- The receiver acknowledges packets in sequence
- If an ACK is not received within the timeout period, the sender retransmits all unacknowledged packets in the window
- A special END_OF_TRANSMISSION packet signals the end of data transfer

### Network Impairment Simulation

The intermediate node simulates:
- **Packet Loss**: Randomly drops packets (configurable probability)
- **Packet Reordering**: Swaps the order of consecutive packets
- **Packet Corruption**: Flips random bits in packets

## Implementation Notes

- Packet size is set to 50 bytes (6 bytes header + 44 bytes payload)
- Network impairment probabilities are set to 10% by default
- mockfile.pdf and test.pdf have been left in the directory to be used for testing the file transmission

## Error Handling

- Corrupted packets are detected via checksum verification, packets get resent after some time
- Timeout mechanism handles lost packets and acknowledgments, packets get resent after some time
- Out-of-order packets are properly managed by the receiver
