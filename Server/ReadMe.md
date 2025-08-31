Secure Data Processing Server

A standalone Java implementation of a secure data ingestion pipeline with agent-server communication, in-memory queuing, and modular processing components.

📋 Overview

This project demonstrates a secure, scalable data processing system built entirely in pure Java without external frameworks. It features TLS-secured communication, payload decryption, intelligent routing, and specialized servers for different data types.

🚀 Architecture
<img width="2144" height="681" alt="secure-data-processing diagram drawio" src="https://github.com/user-attachments/assets/78e0e67d-fe1c-495d-990c-9f40167dbcb6" />

📂 Project Structure
text
```
src/main/java/
├── server/
│   ├── common/               # Shared components
│   │   ├── DataDto.java      # Data transfer object
│   │   ├── DataType.java    # Enumeration of payload types
│   │   └── Config.java       # Server configuration
│   ├── socket/               # Secure socket implementation
│   │   ├── ServerSocket.java
│   │   └── AgentHandler.java
│   ├── queue/                # In-memory queuing system
│   │   ├── MessageQueue.java  # interface
│   │   └── MessageQueueImpl.java
│   ├── manipulation/         # Data processing
│   │   ├── DecryptionEngine.java
│   │   └── ValidationEngine.java
│   ├── router/               # Routing logic
│   │   └── DataRouter.java
│   └── servers/              # Specialized servers
│       ├── FileServer.java
│       ├── ImageServer.java
│       └── LogServer.java
└── Main.java                 # Application entry point
```
⚡ Features

    Pure Java Implementation: No external frameworks or message queues

    TLS-Secured Communication: Encrypted socket connections between agents and server

    In-Memory Buffering: Blocking queue for decoupling ingestion and processing

    Parallel Processing: Thread pool for efficient data handling

    JCA Integration: Java Cryptography Architecture for payload decryption

    Modular Design: Easy to extend with new server types and processing logic

    Payload Validation: Data integrity checks and validation

🛠️ Installation & Usage
Prerequisites

    Java 17 or higher

    Maven 3.6+

    
how a TLS server handles multiple clients with one listening socket and multiple client sockets:
```
                     +------------------+
                     |   ServerSocket   |  <-- Listens on port 
                     +------------------+
                              |
      --------------------------------------------------------
      |                      |                       |
+------------+         +------------+          +------------+
| ClientSocket|         | ClientSocket|        | ClientSocket|
|  (Client A) |         |  (Client B) |        |  (Client C) |
+------------+         +------------+          +------------+
      |                     |                       |
      v                     v                       v
+-------------+       +-------------+        +-------------+
| TLS Handshake|       | TLS Handshake|       | TLS Handshake|
+-------------+       +-------------+        +-------------+
      |                     |                       |
      v                     v                       v
+------------------+   +------------------+   +------------------+
| Multiple Requests |   | Multiple Requests |   | Multiple Requests |
| over same socket |   | over same socket |   | over same socket |
+------------------+   +------------------+   +------------------+

```
✅ Summary Table of server socket 
~~~
| Concept                                                | True/False  |
| ------------------------------------------------------ | ----------- |
| One `ServerSocket` can accept many clients             | ✅ True     |
| One `Socket` can handle many requests from same client | ✅ True     |
| One `Socket` can be shared among clients               | ❌ False    |
| TLS handshake happens per client socket                | ✅ True     |
~~~

🔑 Key Points

Streaming instead of loading:

    We don’t load big files into memory.

    We consume them chunk by chunk via InputStream.

Protocol:

    Client must first send:

    [PayloadType][Size][Data...]

    This way, server knows what’s coming and how many bytes to expect.

Scalability:

    This works for files of GB size without breaking memory.

    Queue holds references to streams, not giant byte arrays.



📦 TCP Segment Format (Header + Data) :
~~~
      0                   1                   2                   3  
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1  
 ┌───────────────────────────────────────────────────────────────┐
 |          Source Port          |       Destination Port        |  32 bits
 ├───────────────────────────────────────────────────────────────┤
 |                        Sequence Number                        |
 ├───────────────────────────────────────────────────────────────┤
 |                    Acknowledgment Number                      |
 ├─────┬─────────┬───┬───────────────────────────────────────────┤
 | HLEN| Reserved|Flags |             Window Size                |
 ├─────┴─────────┴───┴───────────────────────────────────────────┤
 |           Checksum             |        Urgent Pointer        |
 ├───────────────────────────────────────────────────────────────┤
 |                    Options (if any, variable)                 |
 ├───────────────────────────────────────────────────────────────┤
 |                          Data (payload)                       |
 └───────────────────────────────────────────────────────────────┘
~~~
                          <-><-><-><-><-><-><-><-><-><-><-><-> 📦 Packet Structure <-><-><-><-><-><-><-><-><-><-><-><->
                                        
basically describing a situation where your client/server currently just “throw raw data over TLS/TCP,” but you now want to support:

    Different data types (files, text, images, logs, etc.)

    Large payloads (multi-GB files)

    Custom metadata (clientId, machine info, data type, size, etc.)

👉 In this case, yes — it need a protocol (an “application protocol” on top of TLS/TCP).

Why you need a protocol ?

    Framing
        TCP is stream-based, not message-based. If you just write bytes, the server has no idea where one message ends and the next begins. Without framing, large         data will “bleed” into each other.

    Metadata handling
        You need a consistent way to tell the server: “This is file data, size = 2GB, name = foo.mp4, clientId=123, etc.”

    Scalability
        If tomorrow you add more fields or new data types, you don’t want to break compatibility.
        
The solution : "Length-Prefixed JSON + Raw Payload"
We’ll use a two-part message:

        HEADER_LENGTH(4 bytes) | HEADER(JSON string) | PAYLOAD(DATA_SIZE bytes)

1. Header :
    * Length-prefixed JSON (easy to debug & extend).

    * First 4 bytes (big-endian int) → length of JSON header.

    *  Header JSON contains metadata (type, size, etc.)
      
Example header JSON:
~~~
{
  "clientId": "abc123",
  "type": "file",
  "name": "video.mp4",
  "size": 2147483648,
  "chunkSize": 65536,
  "chunkIndex": 0,
  "isLastChunk": false
}
~~~
2. Payload
    * Immediately follows the header.

    * Raw bytes of the data (could be the whole file, or just a chunk).
      
   
🔄 Chunked Transfer Design
For large files, we don’t send everything in one packet. Instead:

    1- Split file into chunks (e.g. 64KB each).

    2- For each chunk:

        Create a header with chunkIndex, chunkSize, isLastChunk.

        Send header + payload.

    3- Server reassembles chunks in order until isLastChunk = true.

This way, you can stream a 2GB file without filling memory.

🔧 Example Transmission

Let’s say client wants to send a 2GB file (video.mp4):

    1) Client splits file into chunks of 64KB.
        → total ≈ 32,768 chunks.

    2) For first chunk:
    
    3) Repeat until last chunk:

        chunkIndex = 32767

        isLastChunk = true

    4) Server writes chunks sequentially to disk.
