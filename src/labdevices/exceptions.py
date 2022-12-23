class CommunicationError(Exception):
    pass

class CommunicationError_ProtocolViolation(CommunicationError):
    pass

class CommunicationError_Timeout(CommunicationError):
    pass

class CommunicationError_NotConnected(CommunicationError):
    pass