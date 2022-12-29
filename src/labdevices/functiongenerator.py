import atexit

from enum import Enum
from .exceptions import CommunicationError_Timeout, CommunicationError_ProtocolViolation

class FunctionGeneratorModulation(Enum):
	NONE = 0
	ASK = 1
	FSK = 2
	PSK = 3
	TRIGGER = 4
	AM = 5
	FM = 6
	PM = 7

class FunctionGeneratorWaveform(Enum):
	SINE = 0
	SQUARE = 1
	RECTANGLE = 2
	TRAPEZOID = 3
	CMOS = 4
	ADJPULSE = 5
	DC = 6
	TRGL = 7
	RAMP = 8
	NEGRAMP = 9
	STAIRTRGL = 10
	STARSTEP = 11
	NEGSTAIR = 12
	POSEXP = 13
	NEGEXP = 14
	PFALLEXP = 15
	NFALLEXP = 16
	POSLOG = 17
	NEGLOG = 18
	PFALLLOG = 19
	NFALLLOG = 20
	PFULLWAV = 21
	NFULLWAV = 22
	PHALFWAV = 23
	NHALFWAV = 24
	SINCPULSE = 26
	IMPULSE = 27
	AM = 28
	FM = 29
	CHIRP = 30
	WHITENOISE = 32
	LORENTZPULSE = 33
	ECGSIMULATION = 34

class FunctionGenerator:
	def __init__(
		self,

		nchannels = None,
		freqrange = ( None, None ),
		amplituderange = ( None, None ),
		offsetrange = ( None, None ),

		arbitraryWaveforms = False,
		hasFrequencyCounter = False,

		supportedWaveforms = [],
		supportedTriggerModes = [],
		supportedModulations = [],

		commandRetries = 3
	):
		if int(nchannels) < 1:
			raise ValueError("A function generator has to have at least one channel")
		if (not isinstance(freqrange, list)) and (not isinstance(freqrange, tuple)):
			raise ValueError("Frequency range has to be either a list or a tuple")
		if (not isinstance(amplituderange, list)) and (not isinstance(amplituderange, tuple)):
			raise ValueError("Amplitude range has to be either a list or a tuple")
		if (not isinstance(offsetrange, list)) and (not isinstance(offsetrange, tuple)):
			raise ValueError("Amplitude range has to be either a list or a tuple")

		if len(freqrange) != 2:
			raise ValueError("Frequency range has to be a 2-tuple or 2-list")
		if (not isinstance(freqrange[0], float)) and (not isinstance(freqrange[0], int)):
			raise ValueError("Frequency range has to be specified with floats or ints")
		if (not isinstance(freqrange[1], float)) and (not isinstance(freqrange[1], int)):
			raise ValueError("Frequency range has to be specified with floats or ints")

		if len(amplituderange) != 2:
			raise ValueError("Amplitude range has to be a 2-tuple or 2-list")
		if (not isinstance(amplituderange[0], float)) and (not isinstance(amplituderange[0], int)):
			raise ValueError("Amplitude range has to be specified with floats or ints")
		if (not isinstance(amplituderange[1], float)) and (not isinstance(amplituderange[1], int)):
			raise ValueError("Amplitude range has to be specified with floats or ints")

		if len(offsetrange) != 2:
			raise ValueError("Offset range has to be a 2-tuple or 2-list")
		if (not isinstance(offsetrange[0], float)) and (not isinstance(offsetrange[0], int)):
			raise ValueError("Offset range has to be specified with floats or ints")
		if (not isinstance(offsetrange[1], float)) and (not isinstance(offsetrange[1], int)):
			raise ValueError("Offset range has to be specified with floats or ints")

		if not isinstance(supportedWaveforms, list):
			raise ValueError("Supported waveforms has to be a list")
		if not isinstance(supportedTriggerModes, list):
			raise ValueError("Supported waveforms has to be a list")
		if not isinstance(supportedModulations, list):
			raise ValueError("Supported waveforms has to be a list")

		for sv in supportedWaveforms:
			if not isinstance(sv, FunctionGeneratorWaveform):
				raise ValueError("Waveform has to be a FunctionGeneratorWaveform instance")
		for sm in supportedModulations:
			if not isinstance(sm, FunctionGeneratorModulation):
				raise ValueError("Modulation has to be a instance of FunctionGeneratorModulation")

		self._nchannels = nchannels
		self._has_arb_waveforms = bool(arbitraryWaveforms)
		self._has_frq_counter = bool(hasFrequencyCounter)

		self._freqrange = freqrange
		self._amprange = amplituderange
		self._offsetrange = offsetrange

		self._supported_waveforms = supportedWaveforms
		self._supported_modulations = supportedModulations
		self._supported_trigger_modes = supportedTriggerModes

		self._commandretries = commandRetries

	# Abstract methods implemented by particular device implementations

	# Connection and off
	def _connect(self):
		raise NotImplementedException()
	def _disconnect(self):
		raise NotImplementedException()
	def _off(self):
		raise NotImplementedException()

	# Identification and serial information
	def _id(self):
		raise NotImplementedException()
	def _serial(self):
		raise NotImplementedException()

	# Channel configuration
	def _set_channel_waveform(self, channel = None, waveform = None):
		raise NotImplementedException()
	def _get_channel_waveform(self, channel = None):
		raise NotImplementedException()
	def _set_channel_frequency(self, channel = None, frequency = None):
		raise NotImplementedException()
	def _get_channel_frequency(self, channel = None):
		raise NotImplementedException()
	def _set_channel_amplitude(self, channel = None, amplitude = None):
		raise NotImplementedException()
	def _get_channel_amplitude(self, channel = None):
		raise NotImplementedException()
	def _set_channel_offset(self, channel = None, offset = None):
		raise NotImplementedException()
	def _get_channel_offset(self, channel = None):
		raise NotImplementedException()
	def _set_channel_duty(self, channel = None, duty = None):
		raise NotImplementedException()
	def _get_channel_duty(self, channel = None):
		raise NotImplementedException()
	def _set_channel_phase(self, channel = None, phase = None):
		raise NotImplementedException()
	def _get_channel_phase(self, channel = None):
		raise NotImplementedException()
	def _set_channel_enabled(self, channel = None, enable = None):
		raise NotImplementedException()
	def _is_channel_enabled(self, channel = None):
		raise NotImplementedException()

	# Public API:
	#
	# ToDo: Implement retry and readback ...

	def connect(self):
		if self._usesContext:
			raise ValueError("Cannot use connect on a context managed (with) object")

		retry_cnt = self._commandretries
		while True:
			try:
				res = self._connect()
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue
			break

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

	def off(self):
		return self._off()

	def identify(self):
		retry_cnt = self._commandretries
		while True:
			try:
				id = self._id()
				return id
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise retry_cnt
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def serial(self):
		retry_cnt = self._commandretries
		while True:
			try:
				return self._serial()
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def set_channel_waveform(self, channel, waveform):
		channel = int(channel)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")
		if not isinstance(waveform, FunctionGeneratorWaveform):
			raise ValueError(f"Supplied waveform {waveform} is not an instance of FunctionGeneratorWaveform")
		if waveform not in self._supported_waveforms:
			raise ValueError(f"The waveform {waveform} is not supported by this particular device")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._set_channel_waveform(channel, waveform)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue
			break

	def get_channel_waveform(self, channel):
		channel = int(channel)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._get_channel_waveform(channel)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def set_channel_frequency(self, channel, frequency):
		channel = int(channel)
		frequency = float(frequency)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		if (frequency < self._freqrange[0]) or (frequency > self._freqrange[1]):
			raise ValueError(f"Requested frequency {frequency}Hz is outside of supported range by this device ({self._freqrange[0]}Hz to {self._freqrange[1]}Hz)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._set_channel_frequency(channel, frequency)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def get_channel_frequency(self, channel):
		channel = int(channel)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._get_channel_frequency(channel)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def set_channel_amplitude(self, channel, amplitude):
		channel = int(channel)
		amplitude = float(amplitude)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")
		if (amplitude < self._amprange[0]) or (amplitude > self._amprange[1]):
			raise ValueError(f"Requested amplitude {amplitude}V is outside supported range from {self._amprange[0]}V to {self._amprange[1]}V")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._set_channel_amplitude(channel, amplitude)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def get_channel_amplitude(self, channel):
		channel = int(channel)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._get_channel_amplitude(channel)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def set_channel_offset(self, channel, offset):
		channel = int(channel)
		offset = float(offset)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")
		if (offset < self._offsetrange[0]) or (offset > self._offsetrange[1]):
			raise ValueError(f"Requested offset {offset}V is outside supported range from {self._offsetrange[0]}V to {self._offsetrange[1]}V")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._set_channel_offset(channel, offset)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def get_channel_offset(self, channel):
		channel = int(channel)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._get_channel_offset(channel)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def set_channel_duty(self, channel, duty):
		channel = int(channel)
		duty = float(duty)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")
		if (duty < 0) or (duty > 100.0):
			raise ValueError(f"Requested duty cycle {duty}% is outside supported range from 0% to 100%")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._set_channel_duty(channel, duty)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def get_channel_duty(self, channel):
		channel = int(channel)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._get_channel_duty(channel)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def set_channel_phase(self, channel, phase):
		channel = int(channel)
		phase = float(phase)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._set_channel_phase(channel, phase)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def get_channel_phase(self, channel):
		channel = int(channel)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._get_channel_phase(channel)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def set_channel_enabled(self, channel, enable):
		channel = int(channel)
		enable = bool(enable)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._set_channel_enabled(channel, enable)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue

	def is_channel_enabled(self, channel):
		channel = int(channel)
		if (channel < 0) or (channel >= self._nchannels):
			raise ValueError(f"Supplied channel index is out of range ({self._nchannels} supported channels)")

		retry_cnt = self._commandretries
		while True:
			try:
				return self._is_channel_enabled(channel, enable)
			except (CommunicationError_Timeout, CommunicationError_ProtocolViolation) as e:
				if retry_cnt == 0:
					raise e
				if retry_cnt > 0:
					retry_cnt = retry_cnt - 1
				continue
