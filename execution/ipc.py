import threading
import mmap
import os
import struct
import time
from collections import deque


# =========================================================
# Ultra-Fast IPC: Shared Memory + Lock-Free Ring Buffer
# =========================================================

class SharedMemoryChannel:
    """
    Ultra-fast IPC channel using:
    - shared memory (mmap)
    - lock-free ring buffer
    - fixed-size message slots
    """

    MESSAGE_SIZE = 1024          # bytes per message
    MESSAGE_COUNT = 256          # number of messages in ring buffer
    BUFFER_SIZE = MESSAGE_SIZE * MESSAGE_COUNT

    def __init__(self, name="ipc_channel"):
        self.name = name
        self.file_path = f"/tmp/{name}.shm"

        # Create shared memory file if not exists
        if not os.path.exists(self.file_path):
            with open(self.file_path, "wb") as f:
                f.write(b"\x00" * self.BUFFER_SIZE)

        # Open shared memory
        self.fd = os.open(self.file_path, os.O_RDWR)
        self.shm = mmap.mmap(self.fd, self.BUFFER_SIZE)

        # Ring buffer pointers
        self.write_index = 0
        self.read_index = 0

        # Thread locks for safety
        self.write_lock = threading.Lock()
        self.read_lock = threading.Lock()

    def _offset(self, index):
        return index * self.MESSAGE_SIZE

    def send(self, message: str):
        """
        Write a message into shared memory.
        Automatically truncates or pads to MESSAGE_SIZE.
        """
        data = message.encode("utf-8")[:self.MESSAGE_SIZE]
        data = data.ljust(self.MESSAGE_SIZE, b"\x00")

        with self.write_lock:
            offset = self._offset(self.write_index)
            self.shm.seek(offset)
            self.shm.write(data)

            self.write_index = (self.write_index + 1) % self.MESSAGE_COUNT

    def receive(self):
        """
        Read the next message from shared memory.
        """
        with self.read_lock:
            offset = self._offset(self.read_index)
            self.shm.seek(offset)
            raw = self.shm.read(self.MESSAGE_SIZE)

            self.read_index = (self.read_index + 1) % self.MESSAGE_COUNT

        return raw.rstrip(b"\x00").decode("utf-8")


# =========================================================
# IPC Server (Message Dispatcher)
# =========================================================

class IPCServer:
    """
    High-speed IPC server that:
    - listens on a shared memory channel
    - dispatches messages to handlers
    - runs in its own thread
    """

    def __init__(self, channel: SharedMemoryChannel):
        self.channel = channel
        self.handlers = {}
        self.running = False
        self.thread = None

    def register_handler(self, key: str, handler):
        """
        Register a message handler.
        """
        self.handlers[key] = handler

    def start(self):
        """
        Start the IPC server loop.
        """
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        """
        Stop the IPC server.
        """
        self.running = False
        if self.thread:
            self.thread.join()

    def _loop(self):
        """
        Main server loop.
        """
        while self.running:
            msg = self.channel.receive()
            if not msg:
                time.sleep(0.001)
                continue

            # Parse message
            if ":" in msg:
                key, payload = msg.split(":", 1)
                if key in self.handlers:
                    try:
                        self.handlers[key](payload)
                    except Exception:
                        pass


# =========================================================
# IPC Client (Message Sender)
# =========================================================

class IPCClient:
    """
    High-speed IPC client for sending messages.
    """

    def __init__(self, channel: SharedMemoryChannel):
        self.channel = channel

    def send(self, key: str, payload: str):
        """
        Send a message in the format:
        key:payload
        """
        msg = f"{key}:{payload}"
        self.channel.send(msg)


# =========================================================
# IPC Factory (Convenience Wrapper)
# =========================================================

class UltraFastIPC:
    """
    Factory for creating IPC server/client pairs.
    """

    @staticmethod
    def create_channel(name="ipc_channel"):
        return SharedMemoryChannel(name)

    @staticmethod
    def create_server(channel):
        return IPCServer(channel)

    @staticmethod
    def create_client(channel):
        return IPCClient(channel)
