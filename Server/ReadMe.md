Secure Data Processing Server

A standalone Java implementation of a secure data ingestion pipeline with agent-server communication, in-memory queuing, and modular processing components.

📋 Overview

This project demonstrates a secure, scalable data processing system built entirely in pure Java without external frameworks. It features TLS-secured communication, payload decryption, intelligent routing, and specialized servers for different data types.

🚀 Architecture

<img width="800" height="600"  alt="deepseek_mermaid_20250827_34536c" src="https://github.com/user-attachments/assets/92242076-c14f-4089-99bc-7b7050932ebc" />

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
                               <-><-><-><-><-><-><-><-><-><-><-><-> Robust packet structure <-><-><-><-><-><-><-><-><-><-><-><->
                                        
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

        HEADER_LENGTH(4 bytes) | HEADER(JSON string) | PAYLOAD(DATA_SIZE bytes)
~~~
{
  "clientId": "abc123",
  "machineIp": "192.168.1.5",
  "os": "Linux",
  "time": "2025-08-31T07:05:00Z",
  "type": "file",
  "name": "big_data.bin",
  "size": 2147483648
}
~~~
 * Easy debugging (you can log headers).

 * Server reads first 4 bytes → knows header size → parse JSON → then read payload.

 * Good for mixed traffic (text, files, etc.).

 * Slight overhead vs binary.
   
Handling Large Files (e.g., 2GB) :

    + Stream payloads in chunks: never buffer whole file in memory.

    + Your protocol should allow chunked transfer:

        Send header (with file metadata & size).

        Then stream payload in e.g. 64KB chunks until size is reached.

    + The server writes chunks directly to disk/queue.
