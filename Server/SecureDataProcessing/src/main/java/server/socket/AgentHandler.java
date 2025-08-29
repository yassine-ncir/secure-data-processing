package server.socket;


import server.common.DataDto;
import server.common.DataType;
import server.queue.MessageQueue;
import server.queue.MessageQueueImpl;

import javax.net.ssl.SSLSocket;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.InputStream;

public class AgentHandler implements Runnable {
    private final SSLSocket socket;
    private final MessageQueue messageQueue = new MessageQueueImpl();

    public AgentHandler(SSLSocket socket) {
        this.socket = socket;
    }


    @Override
    public void run() {
        try (DataInputStream in = new DataInputStream(socket.getInputStream());
             DataOutputStream out = new DataOutputStream(socket.getOutputStream())) {

            socket.startHandshake();

            while (true) {
                // --- Step 1: Read payload type ---
                String typeString;
                try {
                    typeString = in.readUTF(); // client must send type as UTF string
                } catch (Exception e) {
                    System.out.println("Client closed connection.");
                    break;
                }

                DataType type;
                try {
                    type = DataType.valueOf(typeString.toUpperCase());
                } catch (IllegalArgumentException e) {
                    type = DataType.UNKNOWN;
                }

                // --- Step 3: Read size ---
                long size = in.readLong();

                // --- Step 4: Create Payload with stream ---
                InputStream dataStream = socket.getInputStream(); // stream remains open
                DataDto data = new DataDto(dataStream,type, size);

                // Push to queue
                messageQueue.push(data);

                // --- Step 5: Acknowledge ---
                out.writeUTF("ACK: " + type + " (" + size + " bytes)");
                out.flush();

                // ⚠️ Important:
                // Don't read `size` bytes here fully into memory.
                // The consumer (router/server) should stream them chunk by chunk.
            }

        } catch (Exception e) {
            System.err.println("Client disconnected: " + e.getMessage());
        }
    }
}
