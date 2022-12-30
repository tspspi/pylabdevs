# Work in progress
#
# Base class for oscilloscopes

import atexit

from enum import Enum

class OscilloscopeRunMode(Enum):
    RUN = 0,
    STOP = 1
    SINGLE = 2

class OscilloscopeSweepMode(Enum):
    AUTO = 0
    NORMAL = 1
    SINGLE = 2

    @classmethod
    def has_value(cls, v):
        return v in cls._value2member_map_

class OscilloscopeTriggerMode(Enum):
    EDGE = 0
    PULSE = 1
    SLOPE = 2

    @classmethod
    def has_value(cls, v):
        return v in cls._value2member_map_

class OscilloscopeTimebaseMode(Enum):
    MAIN = 0
    XY = 1
    ROLL = 2

    @classmethod
    def has_value(cls, v):
        return v in cls._value2member_map_

class OscilloscopeCouplingMode(Enum):
    DC = 0
    AC = 1
    GND = 2

    @classmethod
    def has_value(cls, v):
        return v in cls._value2member_map_

class Oscilloscope:
    def __init__(
        self,

        nChannels = None,

        supportedSweepModes = [ ],
        supportedTriggerModes = [ ],
        supportedTimebaseModes = [ ],
        supportedRunModes = [ ],
        supportedChannelCouplingModes = [],

        triggerForceSupported = False,

        timebaseScale = ( None, None ),
        voltageScale = ( None, None )
    ):
        if not isinstance(nChannels, int):
            raise ValueError("Channel count has to be an integer")
        if nChannels < 1:
            raise ValueError("Channel count has to be a positive integer")
        if not isinstance(supportedSweepModes, list) and not isinstance(supportedSweepModes, tuple):
            raise ValueError("Sweep modes have to be either list or tuples")
        if not isinstance(supportedTriggerModes, list) and not isinstance(supportedTriggerModes, tuple):
            raise ValueError("Sweep modes have to be either list or tuples")
        if not isinstance(supportedTimebaseModes, list) and not isinstance(supportedTimebaseModes, tuple):
            raise ValueError("Sweep modes have to be either list or tuples")
        if not isinstance(supportedRunModes, list) and not isinstance(supportedRunModes, tuple):
            raise ValueError("Sweep modes have to be either list or tuples")
        if not (isinstance(timebaseScale, tuple) or isinstance(timebaseScale, list)):
            raise ValueError("Timebase scale has to be supplied as list of tuple")
        if not (isinstance(supportedChannelCouplingModes, tuple) or isinstance(supportedChannelCouplingModes, list)):
            raise ValueError("Supported channel coupling modes have to be supplied as list of tuple")
        if not (isinstance(voltageScale, tuple) or isinstance(voltageScale, list)):
            raise ValueError("Voltage scale has to be a tuple or list")

        for rm in supportedRunModes:
            if not isinstance(rm, OscilloscopeRunMode):
                raise ValueError(f"Run mode {rm} not known by labdevs library")
        for rm in supportedSweepModes:
            if not isinstance(rm, OscilloscopeSweepMode):
                raise ValueError(f"Sweep mode {rm} not known by labdevs library")
        for tm in supportedTriggerModes:
            if not isinstance(tm, OscilloscopeTriggerMode):
                raise ValueError(f"Trigger mode {tm} not known by labdevs library")
        for tbm in supportedTimebaseModes:
            if not isinstance(tbm, OscilloscopeTimebaseMode):
                raise ValueError(f"Timebase mode {tbm} not known by labdevs library")
        for chc in supportedChannelCouplingModes:
            if not isinstance(chc, OscilloscopeCouplingMode):
                raise ValueError(f"Coupling mode {chc} is not known by labdevs library")

        if not isinstance(timebaseScale[0], float) and not isinstance(timebaseScale[0], int):
            raise ValueError("Timebase minima and maxima have to be floating point numbers in seconds")
        if not isinstance(timebaseScale[1], float) and not isinstance(timebaseScale[1], int):
            raise ValueError("Timebase minima and maxima have to be floating point numbers in seconds")

        if not isinstance(voltageScale[0], float) and not isinstance(voltageScale[0], int):
            raise ValueError("Voltage scale minimum has to be either float or integer")
        if not isinstance(voltageScale[1], float) and not isinstance(voltageScale[1], int):
            raise ValueError("Voltage scale minimum has to be either float or integer")

        self._usesContext = False
        self._usedConnect = False

        self._nchannels = nChannels
        self._supportedSweepModes = supportedSweepModes
        self._supportedTriggerModes = supportedTriggerModes
        self._supportedTimebaseModes = supportedTimebaseModes
        self._supportedRunModes = supportedRunModes
        self._trigger_force_supported = triggerForceSupported
        self._supportedChannelCouplingModes = supportedChannelCouplingModes

        self._timebase_scale = timebaseScale
        self._voltage_scale = voltageScale

        atexit.register(self._exitOff)

    def _exitOff(self):
        if self._isConnected():
            self.off()


    # Overriden "protected" methods

    def _off(self):
        raise NotImplementedError()
    def _set_trigger_mode(self, mode):
        raise NotImplementedError()
    def _get_trigger_mode(self):
        raise NotImplementedError()
    def _set_sweep_mode(self, mode):
        raise NotImplementedError()
    def _get_sweep_mode(self):
        raise NotImplementedError()
    def _set_run_mode(self, mode):
        raise NotImplementedError()
    def _get_run_mode(self):
        raise NotImplementedError()

    def _set_timebase_mode(self, mode):
        raise NotImplementedError()
    def _get_timebase_mode(self):
        raise NotImplementedError()
    def _set_timebase_scale(self, scale):
        raise NotImplementedError()
    def _get_timebase_scale(self):
        raise NotImplementedError()

    def _identify(self):
        raise NotImplementedError()
    def _isConnected(self):
        raise NotImplementedError()

    def _set_channel_enable(self, channel, enabled):
        raise NotImplementedError()
    def _is_channel_enabled(self, channel):
        raise NotImplementedError()
    def _set_channel_coupling(self, channel, mode):
        raise NotImplementedError()
    def _get_channel_coupling(self, channel):
        raise NotImplementedError()
    def _set_channel_probe_ratio(self, channel, ratio):
        raise NotImplementedError()
    def _get_channel_probe_ratio(self, channel):
        raise NotImplementedError()
    def _set_channel_scale(self, channel, scale):
        raise NotImplementedError()
    def _get_channel_scale(self, channel):
        raise NotImplementedError()

    def _query_waveform(self, channel, stats = None):
        raise NotImplementedError()

    # Public API

    def set_channel_enable(self, channel, enabled):
        if not isinstance(channel, int):
            raise ValueError(f"Channel {channel} is not an integer")
        if (channel < 0) or (channel > self._nchannels):
            raise ValueError(f"Channel {channel} is out of range from 0 to {self._nchannels}")
        if not isinstance(enabled, bool):
            raise ValueError(f"{enabled} is not a boolean argument")

        self._set_channel_enable(channel, enabled)

    def is_channel_enabled(self, channel):
        if not isinstance(channel, int):
            raise ValueError(f"Channel {channel} is not an integer")
        if (channel < 0) or (channel > self._nchannels):
            raise ValueError(f"Channel {channel} is out of range from 0 to {self._nchannels}")

        return self._is_channel_enabled(channel)

    def set_sweep_mode(self, mode):
        if not isinstance(mode, OscilloscopeSweepMode):
            raise ValueError(f"Supplied mode {mode} is not a OscilloscopeSweepMode")

        if mode not in self._supportedSweepModes:
            raise ValueError(f"Sweep mode {mode} not supplied by device")

        self._set_sweep_mode(mode)

    def get_sweep_mode(self):
        return self._get_sweep_mode()

    def set_trigger_mode(self, mode):
        if not isinstance(mode, OscilloscopeTriggerMode):
            raise ValueError(f"Supplied mode {mode} is not a OscilloscopeTriggerMode")

        if mode not in self._supportedTriggerModes:
            raise ValueError(f"Trigger mode {mode} not supplied by device")

        self._set_trigger_mode(mode)

    def get_trigger_mode(self):
        return self._get_trigger_mode()

    def force_trigger(self):
        if self._trigger_force_supported:
            self._force_trigger()
        else:
            raise ValueError("Forcing trigger is not supported by this device")

    def set_timebase_mode(self, mode):
        if not isinstance(mode, OscilloscopeTimebaseMode):
            raise ValueError(f"Supplied mode {mode} is not a OscilloscopeTimebaseMode")
        if mode not in self._supportedTimebaseModes:
            raise ValueError(f"Timebase mode {mode} is not supported by device")
        self._set_timebase_mode(mode)

    def get_timebase_mode(self):
        return self._get_timebase_mode()

    def set_run_mode(self, mode):
        if not isinstance(mode, OscilloscopeRunMode):
            raise ValueError(f"Supplied mode {mode} is not a OscilloscopeRunMode")
        if mode not in self._supportedRunModes:
            raise ValueError(f"Run mode {mode} is not supported by device")

        self._set_run_mode(mode)

    def get_run_mode(self):
        return self._get_run_mode()

    def set_timebase_scale(self, sPerDiv):
        if not isinstance(sPerDiv, float) and not isinstance(sPerDiv, int):
            raise ValueError("Seconds per division has to be a floating point number")
        if (sPerDiv < self._timebase_scale[0]) or (sPerDiv > self._timebase_scale[1]):
            raise ValueError(f"Requested {sPerDiv}s/div is out of range of {self._timebase_scale[0]}s/div and {self._timebase_scale[1]}s/div")

        self._set_timebase_scale(sPerDiv)

    def get_timebase_scale(self):
        return self._get_timebase_scale()

    def set_channel_coupling(self, channel, couplingMode):
        if (channel < 0) or (channel >= self._nchannels):
            raise ValueError(f"Supplied channel {channel} is out of range[0;{self._nchannels-1}]")
        if not isinstance(couplingMode, OscilloscopeCouplingMode):
            raise ValueError(f"Supplied coupling mode {couplingMode} is not a OscilloscopeCouplingMode")
        if couplingMode not in self._supportedChannelCouplingModes:
            raise ValueError(f"Coupling mode {couplingMode} is not supported by the device")

        self._set_channel_coupling(channel, couplingMode)

    def get_channel_coupling(self, channel):
        if (channel < 0) or (channel >= self._nchannels):
            raise ValueError(f"Supplied channel {channel} is out of range [0;{self._nchannels-1}]")

        return self._get_channel_coupling(channel)

    def set_channel_probe_ratio(self, channel, ratio):
        if ratio <= 0:
            raise ValueError(f"Invalid probe ratio {ratio} supplied")
        if (channel < 0) or (channel >= self._nchannels):
            raise ValueError(f"Supplied channel {channel} is out of range [0;{self._nchannels-1}]")
        return self._set_channel_probe_ratio(channel, ratio)

    def get_channel_probe_ratio(self, channel):
        if (channel < 0) or (channel >= self._nchannels):
            raise ValueError(f"Supplied channel {channel} is out of range [0;{self._nchannels-1}]")
        return self._get_channel_probe_ratio(channel)

    def set_channel_scale(self, channel, scale):
        if (channel < 0) or (channel >= self._nchannels):
            raise ValueError(f"Supplied channel {channel} is out of range [0;{self._nchannels-1}]")
        self._set_channel_scale(channel, scale)

    def get_channel_scale(self, channel):
        if (channel < 0) or (channel >= self._nchannels):
            raise ValueError(f"Supplied channel {channel} is out of range [0;{self._nchannels-1}]")
        return self._get_channel_scale(channel)

    def query_waveform(self, channel, stats = None):
        if isinstance(channel, list) or isinstance(channel, tuple):
            # Check each supplied channel is a valid int
            for ch in channel:
                if (int(ch) < 0) or (int(ch) >= self._nchannels) or (int(ch) != ch):
                    raise ValueError(f"Supplied channel {ch} is not valid")
        else:
            channel = int(channel)
            if (channel < 0) or (channel >= self._nchannels):
                raise ValueError(f"Supplied channel {channel} is not valid")

        return self._query_waveform(channel, stats)

    def off(self):
        return self._off()

	# Imperative connect & disconnect methods

    def identify(self):
        return self._identify()

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
