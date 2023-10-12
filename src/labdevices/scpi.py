import socket

from .exceptions import CommunicationError_Timeout, CommunicationError_NotConnected

# SCPI helper class

class SCPIDeviceEthernet:
    def __init__(self, address = None, port = 5025, logger = None):
        if not isinstance(address, str) and not (address is None):
            raise ValueError(f"Address {address} is invalid")
        if not isinstance(port, int):
            raise ValueError("Port has to be an integer value")
        if (port <= 0) or (port > 65535):
            raise ValueError("Port is out of range 1-65535")

        self._address = address
        self._port = port
        self._socket = socket

    def connect(self, address = None, port = None):
        if self._socket is None:
            if address is not None:
                if not isinstance(address, str):
                    raise ValueError(f"Invalid address {address}")
                self._address = address
            if port is not None:
                if not isinstance(port, int):
                    raise ValueError("Port has to be an integer number")
                if (port <= 0) or (port > 65535):
                    raise ValueError("Port number is out of range 1-65535")
                self._port = port

            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self._address, self._port))
        return True

    def disconnect(self):
        if self._socket is not None:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
            self._socket = None

    def isConnected(self):
        if self._socket is not None:
            return True
        else:
            return False

    def scpiQuery(self, query):
        if not self.isConnected():
            raise CommunicationError_NotConnected("Device not connected")
        self._socket.sendall((command + "\n").encode())
        readData = ""

        while True:
            dataBlock = self._socket.recv(4096*10)
            dataBlockStr = dataBlock.decode("utf-8")
            readData = readData + dataBlockStr
            if dataBlockStr[-1] == '\n':
                break

        return readData.strip()

    def scpiCommand(self, command):
        if not self.isConnected():
            raise CommunicationError_NotConnected("Device not connected")
        self._socket.sendall((command + "\n").encode())
        return
