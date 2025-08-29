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
