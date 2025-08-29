package server.common;

public class Config {

    // --- Server Port ---
    public static final int PORT = 8443;

    // --- Thread Pool Size ---
    public static final int THREAD_POOL_SIZE = 10;

    // --- TLS Keystore Settings ---
    public static final String KEYSTORE_PATH = "C:\\Users\\bennc\\Downloads\\gs-securing-web-main\\gs-securing-web-main\\test\\Server\\SecureDataProcessing\\src\\serverkeystore.jks";
    public static final String KEYSTORE_PASSWORD = "changeit";                  // Keystore password
    public static final String KEY_PASSWORD = "changeit";                       // Key password (if different)

    // --- Optional: Max payload size (bytes) ---
    public static final long MAX_PAYLOAD_SIZE = 2L * 1024 * 1024 * 1024; // 2GB

    // --- Optional: TLS Protocol ---
    public static final String TLS_PROTOCOL = "TLS";

    // Private constructor to prevent instantiation
    private Config() {}
}
