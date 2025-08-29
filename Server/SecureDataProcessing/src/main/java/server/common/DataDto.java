package server.common;

import java.io.InputStream;
import java.util.Arrays;

public class DataDto {
    private InputStream data;
    private DataType type;
    private long size;

    // parameter constructor
    public DataDto(InputStream data, DataType type, Long size) {
        this.data = data;
        this.type = type;
        this.size = size;
    }

    // getter & setter
    public InputStream getData() {
        return data;
    }

    public DataType getType() {
        return type;
    }

    public Long getSize(){
        return size;
    }

    // to string

    @Override
    public String toString() {
        return "{" +
                "data= " + data +
                ", type= " + type +
                ", size= " + size +
                '}';
    }
}
