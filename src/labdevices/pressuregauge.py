import atexit

from enum import Enum

class PressureGaugeUnit(Enum):
    MBAR = 0
    PASCAL = 1
    TORR = 2

class PressureGauge:
    def __init__(
        self,
        measurementRange = ( None, None ),
        hasDegas = False,
        deviceSupportedUnits = [ PressureGaugeUnit.MBAR ],
        debug = False
    ):
        if not isinstance(measurementRange, tuple) and not isinstance(measurementRange, list):
            raise ValueError("Measurement range has to be tuple or list with two components")
        if len(measurementRange) != 2:
            raise ValueError("Measurement range can only have two component")
        if measurementRange[0] > measurementRange[1]:
            raise ValueError("Measurement range minimum is larger than maximum")
        if len(deviceSupportedUnits) < 1:
            raise ValueError("Measurement units of device are unknown")

        self._debug = debug

        self._usesContext = False
        self._usedConnect = False

        self._supportedUnits = deviceSupportedUnits
        self._hasDegas = hasDegas

    # Overriden methods

    def _get_serials(self):
        return None
    def _get_versions(self):
        raise NotImplementedError()

    def _get_device_type(self):
        raise NotImplementedError()

    def _degas(self, degasOn):
        raise NotImplementedError()

    def _get_pressure(self):
        raise NotImplementedError()

    def _get_unit(self):
        raise NotImplementedError()

    def _set_unit(self, unit):
        raise NotImplementedError()

    # Public methods

    def get_pressure(self, unit = PressureGaugeUnit.MBAR):
        if not isinstance(unit, PressureGaugeUnit):
            raise ValueError("Unit has to be one the supported pressuage gauge units")

        resp = self._get_pressure()

        if resp is None:
            return None

        if unit in resp['value']:
            return resp['value'][unit]

        # Check if we can perform the conversion from MBAR to the given unit
        if unit == PressureGaugeUnit.MBAR:
            return resp['mbar']
        elif unit == PressureGaugeUnit.TORR:
            return resp['mbar'] * 0.750062
        elif unit == PressureGaugeUnit.PASCAL:
            return resp['mbar'] * 100.0
        else:
            raise ValueError(f"Unknown unit {unit}")

    def get_device_serial(self):
        raise NotImplementedError()

    def get_unit(self):
        return self._get_unit()

    def set_unit(self, unit = PressureGaugeUnit.MBAR):
        if not isinstance(unit, PressureGaugeUnit):
            raise ValueError(f"Unit {unit} is not instance of PressureGaugeUnit")
        if unit not in self._supportedUnits:
            raise ValueError(f"Unit {unit} not supported by device (supported: {self._supportedUnits})")
        return self._set_unit(unit)

    def degas(self, degasOn = True):
        if not isinstance(degasOn, bool):
            raise ValueError("Enable or disable parameter has to be a boolean")

        if self._hasDegas:
            self._degas(degasOn)
        else:
            raise NotImplementedError("Device does not support degas")

    def connect(self):
        if self._usesContext:
            raise ValueError("Cannot use connect on a context managed (with) object")

        res = self._connect()
        if not res:
            return res

        self._usedConnect = True
        return True

    def disconnect(self):
        if self._usesContext:
            raise ValueError("Cannot use connect on a context managed (with) object")
        if not self._usedConnect:
            return True

        self._disconnect()
        self._usedConnect = False
        return True
