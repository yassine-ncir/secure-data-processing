package server.socket;

import server.common.Config;

import javax.net.ssl.*;
import java.io.FileInputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyStore;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ServerSocket {

    private final int port;
    private final int threadPoolSize;
    private SSLServerSocket serverSocket;
    private ExecutorService threadPool;


    public ServerSocket(int port, int threadPoolSize) {
        this.port = port;
        this.threadPoolSize = threadPoolSize;
    }

    public void start() throws Exception {
        // --- Step 1: Load Keystore ---
        KeyStore ks = KeyStore.getInstance("JKS");
        ks.load(Files.newInputStream(Paths.get(Config.KEYSTORE_PATH)), Config.KEYSTORE_PASSWORD.toCharArray());

        // --- Step 2: Initialize Key Manager ---
        KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
        kmf.init(ks, Config.KEYSTORE_PASSWORD.toCharArray());

        // --- Step 3: Initialize TLS Context ---
        SSLContext sc = SSLContext.getInstance("TLS");
        sc.init(kmf.getKeyManagers(), null, null);

        // --- Step 4: Create SSL Server Socket ---
        SSLServerSocketFactory ssf = sc.getServerSocketFactory();
        serverSocket = (SSLServerSocket) ssf.createServerSocket(port);
        System.out.println("Secure TLS Server started on port " + port);

        // --- Step 5: Initialize thread pool ---
        threadPool = Executors.newFixedThreadPool(threadPoolSize);

        // --- Step 6: Accept client connections ---
        while (true) {
            SSLSocket AgentSocket = (SSLSocket) serverSocket.accept();
            System.out.println("New client connected: " + AgentSocket.getInetAddress());

            // Submit client handler to thread pool
            threadPool.submit(new AgentHandler(AgentSocket));
        }
    }

    public void stop() throws Exception {
        if (serverSocket != null && !serverSocket.isClosed()) {
            serverSocket.close();
        }
        if (threadPool != null && !threadPool.isShutdown()) {
            threadPool.shutdown();
        }
        System.out.println("Secure TLS Server stopped.");
    }
}
