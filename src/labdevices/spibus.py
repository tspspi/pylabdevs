from enum import Enum

class SPIClockPolarity:
    IDLE_LOW = 0x00
    IDLE_HIGH = 0x02

class SPIClockPhase:
    LEADING_EDGE = 0x00
    TRAILING_EDGE = 0x01

class SPIBus:
    def __init__(self):
        pass

    # Abstract (overriden) methods

    def _getClockSpeed(self):
        raise NotImplementedError()
    def _setClockSpeed(self, hz):
        raise NotImplementedError()
    def _getMode(self):
        raise NotImplementedError()
    def _setMode(self, clockPolarity = None, clockPhase = None):
        raise NotImplementedError()
    def _transfer(self, nbytes = None, buffer = None):
        raise NotImplementedError()

    # Exposed methods

    def getClockSpeed(self):
        return self._getClockSpeed()
    def setClockSpeed(self, hz):
        if (int(hz) <= 0):
            raise ValueError("Clock frequency has to be a positive integer")
        self._setClockSpeed(hz)
    def getMode(self):
        return self._getMode()
    def setMode(self, clockPolarity = None, clockPhase = None):
        if (clockPolarity is None) and (clockPhase is None):
            return True
        if not isinstance(clockPolarity, SPIClockPolarity):
            raise ValueError("Clock polarity has to be a SPIClockPolarity instance")
        if not isinstance(clockPhase, SPIClockPhase):
            raise ValueError("Clock phase has to be a SPIClockPhase instance")

        self._setMode(clockPolarity, clockPhase)
    def transfer(self, nbytes = None, buffer = None):
        if (nbytes is None) and (buffer is None):
            raise ValueError("Length of transfer is not determinable without nbytes or a TX buffer")

        if (nbytes is not None) and (buffer is not None):
            if len(buffer) != nbytes:
                raise ValueError(f"Supplied length {nbytes} differs from buffer length {len(buffer)}")

        if buffer is not None:
            nbytes = len(buffer)
            buffer = bytes(buffer)
            if not isinstance(buffer, bytes):
                raise ValueError("Buffer has to be a bytes instance ...")
        else:
            # Buffer does not exist ...
            buffer = bytes( [ 0 ] * nbytes )

        return self._transfer(nbytes, buffer)
