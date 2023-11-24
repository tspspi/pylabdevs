import atexit
import logging

from enum import Enum
from abc import abstractmethod

class RFPowerLevel(Enum):
    dBm = 0
    dBmV = 1
    dBuV = 2
    V = 3
    W = 4

class SpectrumAverageUnit(Enum):
    PowerLog = 0
    Power = 1
    Voltage = 2

class SpectrumAnalyzer:
    def __init__(
        self,

        channels = 1,

        frequencyRange = ( None, None ),

        hasPreamp = False,
        hasTrackingGenerator = False,

        inputAttenuator = ( None, None ),
        resolutionBandwidth = ( None, None ),
        referenceLevel = ( None, None ),
        attenuator = ( None, None ),
        offset = ( None, None ),

        loglevel = logging.ERROR,
        logger = None
    ):
        channels = int(channels)
        if (channels < 1):
            raise ValueError("Spectrum analyzer has to have at least one channel")

        if not isinstance(frequencyRange, tuple) and not isinstance(frequencyRange, list):
            raise ValueError("Frequency range has to be tuple or list")
        if not isinstance(inputAttenuator, tuple) and not isinstance(inputAttenuator, list):
            raise ValueError("Input attenuator range has to be tuple or list")
        if not isinstance(resolutionBandwidth, tuple) and not isinstance(resolutionBandwidth, list):
            raise ValueError("Resolution bandwidth range has to be tuple or list")
        if not isinstance(referenceLevel, tuple) and not isinstance(referenceLevel, list):
            raise ValueError("Reference level range has to be tuple or list")
        if not isinstance(offset, tuple) and not isinstance(offset, list):
            raise ValueError("Offset range has to be tuple or list")

        if (len(frequencyRange) != 2) or (len(inputAttenuator) != 2) or (len(resolutionBandwidth) != 2) or (len(referenceLevel) != 2) or (len(offset) != 2):
            raise ValueError("The ranges (frequency, input attenuator, resolution bandwidth, reference level, attenuator range, offset range) have to contain minimum and maximum (2 elements)")

        if frequencyRange[0] > frequencyRange[1]:
            raise ValueError("Minimum frequency is larger than maximum frequency")
        if inputAttenuator[0] > inputAttenuator[1]:
            raise ValueError("Input attenuator minimum is larger than maximum")
        if resolutionBandwidth[0] > resolutionBandwidth[1]:
            raise ValueError("Minimum RBW is larger than maximum")
        if referenceLevel[0] > referenceLevel[1]:
            raise ValueError("Minimum reference level is larger than maximum")
        if offset[0] > offset[1]:
            raise ValueError("Minimum offset is larger than maximum")


        self._frequencyRange = frequencyRange
        self._inputAttenuatorRange = inputAttenuator
        self._resolutionBandwidthRange = resolutionBandwidth
        self._referenceLevelRange = referenceLevel
        self._offsetRange = offset
        self._channels = channels

        self._hasTrackingGenerator = hasTrackingGenerator
        self._hasPreamp = hasPreamp

        if logger is not None:
            self._logger = logger
        else:
            self._logger = logging.getLogger(__name__)
            self._logger.addHandler(logging.StreamHandler(sys.stdout))
            self._logger.setLevel(loglevel)

    # Abstract methods

    @abstractmethod
    def _set_frequency_range(self, start = None, stop = None):
        raise NotImplementedError()
    @abstractmethod
    def _set_frequency_center(self, center = None, span = None):
        raise NotImplementedError()
    @abstractmethod
    def _get_frequency_range(self):
        raise NotImplementedError()
    @abstractmethod
    def _get_frequency_center(self):
        raise NotImplementedError()
    @abstractmethod
    def _id(self):
        raise NotImplementedError()
    @abstractmethod
    def _set_reference_level(self, rlevel = None, channel = 1):
        raise NotImplementedError()
    @abstractmethod
    def _get_reference_level(self, channel = 1):
        raise NotImplementedError()


    def set_frequency_range(self, start = None, stop = None):
        if (start is None) and (stop is None):
            self._logger.debug("Called set frequency range without start and stop. Ignoring")
            return True

        if start is not None:
            start = float(start)
            if not ((start >= self._frequencyRange[0]) and (self._frequencyRange[1] <= start)):
                self._logger.error(f"Set frequency range called, start {start} is out of range {self._frequencyRange}")
                raise ValueError("Start out of supported frequency range")
        if stop is not None:
            stop = float(stop)
            if not ((stop >= self._frequencyRange[0]) and (self._frequencyRange[1] <= stop)):
                self._logger.error(f"Set frequency range called, stop {stop} is out of range {self._frequencyRange}")
                raise ValueError("Stop out of supported frequency range")

        self._logger.debug(f"Setting frequency range from {start} to {stop}")
        return self._set_frequency_range(start, stop)

    def set_frequency_center(self, center = None, span = None):
        if (center is None) and (span is None):
            self._logger.debug("Called set frequency center called without center and span. Ignoring")
            return True

        if center is not None:
            center = float(center)
            if not ((center >= self._frequencyRange[0]) and (self._frequencyRange[1] <= center)):
                self._logger.error(f"Center frequency {center} out of supported range {self._frequencyRange}")
                raise ValueError(f"Center frequency {center} out of supported range {self._frequencyRange}")

        if span is not None:
            span = float(span)

        if (center is not None) and (span is not None):
            st, sp = center - span, center + span
            if not ((st >= self._frequencyRange[0]) and (self._frequencyRange[1] <= st)):
                self._logger.error(f"Minimum frequency {st} not in supported range {self._frequencyRange}")
                raise ValueError(f"Minimum frequency {st} not in supported range {self._frequencyRange}")
            if not ((sp >= self._frequencyRange[0]) and (self._frequencyRange[1] <= sp)):
                self._logger.error(f"Maximum frequency {sp} not in supported range {self._frequencyRange}")
                raise ValueError("Maximum frequency {sp} not in supported range {self._frequencyRange}")

        self._logger.debug(f"Setting center to {center} and span to {span}")
        return self._set_frequency_center(center, span)

    def get_version(self):
        self._logger.debug("Querying ID")
        return self._id()['version']
    def get_serial(self):
        self._logger.debug("Querying ID")
        return self._id()['serial']
    def get_type(self):
        self._logger.debug("Querying ID")
        return self._id()['type']
    def get_id(self):
        self._logger.debug("Querying ID")
        return self._id()

    def get_frequency_range(self):
        self._logger.debug("Querying frequency range")
        return self._get_frequency_range()
    def get_frequency_center(self):
        self._logger.debug("Querying frequency center and span")
        return self._get_frequency_center()

    def set_reference_level(self, rlevel = None, channel = 0):
        channel = int(channel)
        if (channel < 0) or (channel >= self._channels):
            self._logger.error(f"Channel {channel} out of range {self._channels}")
            raise ValueError(f"Channel {channel} out of range {self._channels}")

        if rlevel is None:
            self._logger.debug("Setting reference level called without reference level. Ignoring")
            return True

        rlevel = float(rlevel)
        if not ((rlevel >= self._referenceLevelRange[0]) and (self._referenceLevelRange[1] >= rlevel)):
            self._logger.error(f"Setting reference level called with {rlevel} out of range {self._referenceLevelRange}")
            raise ValueError(f"Reference level {rlevel} out of range {self._referenceLevelRange}")

        self._logger.debug(f"Setting reference level to {rlevel} on channel {channel}")
        return self._set_reference_level(rlevel, channel)

    def get_reference_level(self, channel = 0):
        self._logger.debug(f"Querying reference level on channel {channel}")
        return self._get_reference_level(channel)

    def set_input_attenuation(self, attenuator = None):
        pass
    def get_input_attenuation(self):
        pass

    def set_preamp_enable(self, enabled = True):
        pass
    def get_preamp_enable(self):
        pass

    def set_amplitude_unit(self, unit = RFPowerLevel.dBm):
        pass
    def get_amplitude_unit(self):
        pass

    def set_resolution_bandwidth(self, rbw = None):
        pass
    def get_resolution_bandwidth(self):
        pass

    def set_average(self, avgs = 0, unit = SpectrumAverageUnit.PowerLog):
        pass
    def get_average(self):
        pass

    def set_offset(self, offset = None):
        pass
    def get_offset(self):
        pass

    def query_trace(self, trace = 0):
        pass

