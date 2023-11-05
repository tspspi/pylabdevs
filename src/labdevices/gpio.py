from enum import Enum

class GpioDirection(Enum):
    INPUT   = 0x01
    OUTPUT  = 0x02
    MASK    = 0x01|0x02

class GpioDrive(Enum):
    OPENDRAIN   = 0x04
    PUSHPULL    = 0x08
    TRISTATE    = 0x10
    MASK        = 0x04|0x08|0x10

class GpioPulls(Enum):
    PULLUP      = 0x20
    PULLDOWN    = 0x40
    MASK        = 0x20|0x40

class GPIO:
    def __init__(
        self,
        numberOfPins
    ):
        self._maxio = numberOfPins

    # Abstract methods that should be implemented by any implementation

    def _getConfig(self, pin):
        raise NotImplementedError()
    def _setConfig(self, pin):
        raise NotImplementedError()
    def _set(self, pin, status):
        raise NotImplementedError()
    def _get(self, pin):
        raise NotImplementedError()
    def _pulse(self, pin, microseconds, state = None):
        raise NotImplementedError()

    # Public methods available to any user instance

    def getIOCount(self):
        return self._maxio

    def getConfig(self, pin):
        if (pin >= self._maxio) or (pin < 0):
            raise ValueError(f"Pin number {pin} is outside of supported range from 0 to {self._maxio-1}")

        return self._getConfig(pin)

    def setConfig(
        self,
        pin,
        name = None,
        direction = None,
        pull = None,
        drive = None,
        invertInput = False,
        invertOutput = False,
        hardwarePulsate = False
    ):
        if (pin < 0) or (pin >= self._maxio):
            raise ValueError(f"Pin number {pin} is outside of supported range from 0 to {self._maxio-1}")

        return self._setConfig(pin, name, direction, pull, drive, invertInput, invertOutput, hardwarePulsate)

    def set(self, pin, status):
        if (pin < 0) or (pin >= self._maxio):
            raise ValueError(f"Pin number {pin} outside of supported range from 0 to {self._maxio-1}")

        return self._set(pin, status)

    def get(self, pin):
        if (pin < 0) or (pin >= self._maxio):
            raise ValueError(f"Pin number {pin} outside of supported range from 0 to {self._maxio-1}")

        return self._get(pin)

    def pulse(self, pin, microseconds, state = None):
        if (pin < 0) or (pin >= self._maxio):
            raise ValueError(f"Pin number {pin} outside of supported range from 0 to {self._maxio-1}")

        return self._pulse(pin, microseconds, state)

