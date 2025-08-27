🔒 Secure Data Processing Server

A standalone agent → server pipeline built in pure Java (no frameworks, no external MQs).
This project demonstrates how to design and implement a modular, maintainable, and scalable data ingestion system.

🚀 Architecture

Flow:

Components :

1) Secure Socket Server: Accepts agent connections and reads data.

2) Queue (In-Memory): Buffers incoming payloads for decoupling.

3) Data Manipulation Layer: Decrypts payloads with JCA and validates.

4) Router: Determines target server (File, Image, Log).

5) Servers:

      FileServer – handles file payloads.

      ImageServer – handles image payloads.

      LogServer – handles log payloads.


📂 Project Structure

src/main/java/
   ├── agent/                  # Agent-side code (client + encryption)
   ├── server/
   │    ├── common/            # Shared DTOs, enums, config
   │    ├── socket/            # TLS socket server + client handlers
   │    ├── queue/             # In-memory message queue + worker pool
   │    ├── manipulation/      # JCA decryption + validation
   │    ├── router/            # Routing to proper server
   │    └── servers/           # FileServer, ImageServer, LogServer
   └── Main.java               # Entry point


⚡ Features

Standalone Java (no frameworks).

TLS-secured socket server.

In-memory blocking queue for buffering.

Thread pool for parallel data processing.

Modular design for extensibility (add new servers easily).

JCA-based payload decryption (plug in your crypto logic).
