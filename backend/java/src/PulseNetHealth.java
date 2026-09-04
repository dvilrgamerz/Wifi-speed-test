import java.time.Instant;

/** Lightweight Java health client/model for native integrations. */
public final class PulseNetHealth {
    private PulseNetHealth() {}

    public static String healthJson() {
        return "{\"status\":\"ok\",\"service\":\"pulsenet-java\",\"timestamp\":\""
                + Instant.now() + "\"}";
    }
}
