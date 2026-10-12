"""Common interface for single- and multi-channel ion-pump controllers.

Channels are numbered from one. Closing a connection never stops a pump.
Optional controller operations raise NotImplementedError when unsupported.
"""

import math

from .pressuregauge import PressureGaugeUnit


class IonPump:
    def __init__(self, nChannels = 1, defaultChannel = 1,
                 voltageRange = None, debug = False):
        if isinstance(nChannels, bool) or not isinstance(nChannels, int) or nChannels < 1:
            raise ValueError("Number of channels must be a positive integer")
        self._nChannels = nChannels
        self._defaultChannel = self._validate_channel(defaultChannel)
        if voltageRange is not None:
            if len(voltageRange) != 2 or not all(
                    isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
                    for v in voltageRange) or voltageRange[0] > voltageRange[1]:
                raise ValueError("Voltage range must contain finite ordered minimum and maximum")
        self._voltageRange = voltageRange
        self._debug = debug
        self._usesContext = False
        self._usedConnect = False

    def _validate_channel(self, channel):
        if isinstance(channel, bool) or not isinstance(channel, int) or not 1 <= channel <= self._nChannels:
            raise ValueError(f"Channel must be an integer from 1 to {self._nChannels}")
        return channel

    def _channel(self, channel):
        return self._defaultChannel if channel is None else self._validate_channel(channel)

    def get_channel_count(self):
        return self._nChannels

    def get_default_channel(self):
        return self._defaultChannel

    def set_default_channel(self, channel):
        self._defaultChannel = self._validate_channel(channel)

    def _connect(self):
        raise NotImplementedError()

    def _disconnect(self):
        raise NotImplementedError()

    def _is_connected(self):
        raise NotImplementedError()

    def _identify(self):
        raise NotImplementedError()

    def _start(self, channel):
        raise NotImplementedError()

    def _stop(self, channel):
        raise NotImplementedError()

    def _restart(self, channel):
        raise NotImplementedError()

    def _clear_alarms(self, channel):
        raise NotImplementedError()

    def _get_status(self, channel):
        raise NotImplementedError()

    def _get_measurement(self, channel):
        raise NotImplementedError()

    def _get_voltage(self, channel):
        raise NotImplementedError()

    def _get_current(self, channel):
        raise NotImplementedError()

    def _get_voltage_setpoint(self, channel):
        raise NotImplementedError()

    def _set_voltage(self, voltage, channel):
        raise NotImplementedError()

    def _get_pump_size(self, channel):
        raise NotImplementedError()

    def connect(self):
        if self._usesContext:
            raise ValueError("Cannot connect a context managed object")
        result = self._connect()
        self._usedConnect = bool(result)
        return result

    def disconnect(self):
        if self._usesContext:
            raise ValueError("Cannot disconnect a context managed object; use close")
        return self.close()

    def close(self):
        try:
            return self._disconnect()
        finally:
            self._usedConnect = False

    def is_connected(self):
        return self._is_connected()

    def __enter__(self):
        if self._usedConnect or self._usesContext:
            raise ValueError("Cannot enter context on an already connected object")
        if not self._connect():
            raise ConnectionError("Connection failed")
        self._usesContext = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.close()
        finally:
            self._usesContext = False

    def identify(self):
        return self._identify()

    def start(self, channel = None):
        return self._start(self._channel(channel))

    def stop(self, channel = None):
        return self._stop(self._channel(channel))

    def restart(self, channel = None):
        return self._restart(self._channel(channel))

    def clear_alarms(self, channel = None):
        return self._clear_alarms(self._channel(channel))

    def get_status(self, channel = None):
        """Return controller state, including enabled, need_restart and alarms."""
        return self._get_status(self._channel(channel))

    def get_measurement(self, channel = None):
        """Return timestamped voltage_V, current_A, pressure_mbar and channel.

        Unavailable pressure is None, never a fabricated zero-pressure value.
        Communication failures raise exceptions rather than return stale data.
        """
        return self._get_measurement(self._channel(channel))

    def get_voltage(self, channel = None):
        return self._get_voltage(self._channel(channel))

    def get_current(self, channel = None):
        return self._get_current(self._channel(channel))

    def get_pressure(self, unit = PressureGaugeUnit.MBAR, channel = None):
        if not isinstance(unit, PressureGaugeUnit):
            raise ValueError("Unit must be a PressureGaugeUnit")
        pressure = self.get_measurement(channel)["pressure_mbar"]
        if pressure is None:
            return None
        return pressure * {PressureGaugeUnit.MBAR: 1,
                           PressureGaugeUnit.TORR: 0.750061683,
                           PressureGaugeUnit.PASCAL: 100}[unit]

    def get_voltage_setpoint(self, channel = None):
        return self._get_voltage_setpoint(self._channel(channel))

    def set_voltage(self, voltage, channel = None):
        channel = self._channel(channel)
        if isinstance(voltage, bool) or not isinstance(voltage, (int, float)) or not math.isfinite(voltage):
            raise ValueError("Voltage must be a finite number")
        if self._voltageRange is not None and not self._voltageRange[0] <= voltage <= self._voltageRange[1]:
            raise ValueError("Voltage is outside the supported range")
        return self._set_voltage(voltage, channel)

    def get_pump_size(self, channel = None):
        """Optional configured pumping speed in litres per second."""
        return self._get_pump_size(self._channel(channel))
