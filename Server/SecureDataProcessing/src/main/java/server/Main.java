package server;

import server.common.DataDto;
import server.common.DataType;
import server.queue.MessageQueue;
import server.queue.MessageQueueImpl;

import server.common.Config;
import server.socket.ServerSocket;

public class Main {
    public static void main(String[] args) {
        ServerSocket server = new ServerSocket(Config.PORT, Config.THREAD_POOL_SIZE);

        // Add shutdown hook to close server gracefully
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try {
                System.out.println("Shutting down server...");
                server.stop();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }));

        try {
            System.out.println("Starting TLS server...");
            server.start();
        } catch (Exception e) {
            System.err.println("Server failed to start: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
