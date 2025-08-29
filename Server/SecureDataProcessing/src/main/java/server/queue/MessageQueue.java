package server.queue;

import server.common.DataDto;

public interface MessageQueue {
    // push
    void push(DataDto dto) throws InterruptedException;
    // pull
    DataDto pop() throws InterruptedException;
    // MessagesNb
    int messagesNb();
}
