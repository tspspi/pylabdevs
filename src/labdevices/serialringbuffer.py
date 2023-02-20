# A simple (synchronizing) serial ringbuffer used in some
# lab device implementations.

# This is a simple helper class

import threading
from collections import deque

class SerialRingBuffer:
    def __init__(self, bufferSize = 512):
        self.bufferSize = bufferSize
        self.buffer = [ ]
        for i in range(512):
            self.buffer.append(None)
        self.head = 0
        self.tail = 0
        self.lock = threading.Lock()

    def isAvailable(self, *ignore, blocking = True):
        if blocking:
            self.lock.acquire()
        if self.head == self.tail:
            if blocking:
                self.lock.release()
            return False
        else:
            if blocking:
                self.lock.release()
            return True

    def available(self, *ignore, blocking = True):
        if blocking:
            self.lock.acquire()
        res = 0
        if self.head >= self.tail:
            res = self.head - self.tail;
        else:
            res = self.bufferSize - self.tail + self.head
        if blocking:
            self.lock.release()
        return res

    def discard(self, len, *ignore, blocking = True):
        if blocking:
            self.lock.acquire()
        avail = self.available(blocking = False)
        if avail < len:
            self.tail = (self.tail + avail) % self.bufferSize
        else:
            self.tail = (self.tail + len) % self.bufferSize
        if blocking:
            self.lock.release()
        return None

    def peek(self, distance, *ignore, blocking = True):
        if blocking:
            self.lock.acquire()
        if distance >= self.available(blocking = False):
            if blocking:
                self.lock.release()
            return None
        else:
            res = self.buffer[(self.tail + distance) % self.bufferSize]
            if blocking:
                self.lock.release()
            return res

    def remainingCapacity(self, *ignore, blocking = True):
        if blocking:
            self.lock.acquire()
        res = self.bufferSize - self.available(blocking = False) - 1
        if blocking:
            self.lock.release()
        return res

    def capacity(self, *ignore, blocking = True):
        return self.bufferSize

    def push(self, data, *ignore, blocking = True):
        if blocking:
            self.lock.acquire()
        if isinstance(data, list):
            if self.remainingCapacity(blocking = False) <  len(data):
                # Raise error ... ToDo
                if blocking:
                    self.lock.release()
                return
            else:
                for c in data:
                    self.push(c, blocking = False)
        else:
            if self.remainingCapacity(blocking = False) < 1:
                # Raise error ... ToDo
                if blocking:
                    self.lock.release()
                return
            self.buffer[self.head] = data
            self.head = (self.head + 1) % self.bufferSize
        self.lock.release()

    def pop(self, *ignore, blocking = True):
        if blocking:
            self.lock.acquire()
        ret = None
        if self.head != self.tail:
            ret = self.buffer[self.tail]
            self.tail = (self.tail + 1) % self.bufferSize
        if blocking:
            self.lock.release()
        return ret

    def read(self, len, *ignore, blocking = True):
        if blocking:
            self.lock.acquire()
        if self.available(blocking = False) < len:
            # ToDo Raise exception
            if blocking:
                self.lock.release()
            return None
        ret = [ ]
        for i in range(len):
            ret.append(self.buffer[(self.tail + i) % self.bufferSize])
        self.tail = (self.tail + len) % self.bufferSize
        if blocking:
            self.lock.release()
        return ret
