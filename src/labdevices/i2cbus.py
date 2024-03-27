class I2CBus:
    def __init__(self):
        pass

    def scan(self):
        raise NotImplementedError()
    def read(self, device, nbytes, raiseException = False):
        raise NotImplementedError()
    def write(self, device, data, raiseException = False):
        raise NotImplementedError()
