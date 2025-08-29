package server.queue;

import server.common.DataDto;

import java.util.concurrent.LinkedBlockingQueue;

public class MessageQueueImpl implements MessageQueue{
    private final LinkedBlockingQueue<DataDto> queue = new LinkedBlockingQueue<>();


    @Override
    public void push(DataDto data) throws InterruptedException {
        queue.put(data);
    }

    @Override
    public DataDto pop() throws InterruptedException {
        return queue.take();
    }

    @Override
    public int messagesNb() {
        return queue.size();
    }
}
