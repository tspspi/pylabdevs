import atexit

from enum import Enum

class PowerSupplyLimit(Enum):
	NONE = 0
	VOLTAGE = 1
	CURRENT = 2

class PowerSupply:
	def __init__(
		self,
		nChannels = None,
		vrange = None,
		arange = None,
		prange = None,
		capableVLimit = True,
		capableALimit = True,
		capableMeasureV = True,
		capableMeasureA = True,
		capableOnOff = True
	):
		if not isinstance(nChannels, int):
			raise ValueError("Number of channels required")
		if nChannels < 1:
			raise ValueError("Power supply has to support at least one channel")
		if (vrange is None) or (arange is None) or (prange is None):
			raise ValueError("Voltage, current and power range has to be supplied")
		if (not isinstance(vrange, tuple)) or (not isinstance(arange, tuple)) or (not isinstance(prange, tuple)):
			raise ValueError("Voltage, current and power ranges have to be tuples")
		if (len(vrange) != 3) or (len(arange) != 3) or (len(prange) != 3):
			raise ValueError("Ranges have to supply minimum, maximum and step size")

		self._usesContext = False
		self._usedConnect = False

		self._nchannels = nChannels
		self._vrange = vrange
		self._arange = arange
		self._prange = prange
		self._capabilities = {
			'vlimit' : capableVLimit,
			'alimit' : capableALimit,
			'measureV' : capableMeasureV,
			'measureA' : capableMeasureA,
			'onoff' : capableOnOff
		}

		# Note that implementations have to update _setValues themselves!!
		self._setValues = []
		for i in range(nChannels):
			self._setValues.append({
				'onoff' : False,
				'volts' : 0.0,
				'amps' : 0.0
			})

		# We ensure calling "off" whenever the process gets terminated ...
		atexit.register(self._exitOff)

	def _exitOff(self):
		if self._isConnected():
			self.off()

	def _setChannelEnable(self, enable, channel):
		raise NotImplementedError()
	def _setVoltage(self, voltage, channel):
		raise NotImplementedError()
	def _setCurrent(self, current, channel):
		raise NotImplementedError()
	def _getVoltage(self, channel):
		raise NotImplementedError()
	def _getCurrent(self, channel):
		raise NotImplementedError()
	def _off(self):
		raise NotImplementedError()
	def _getLimitMode(self, channel):
		raise NotImplementedError()
	def _isConnected(self):
		raise NotImplementedError()
	def _connect(self):
		raise NotImplementedError()
	def _disconnect(self):
		raise NotImplementedError()

	def setChannelEnable(self, enable, channel = 1):
		if not isinstance(channel, int):
			raise ValueError("Channel has to be an integer number")
		if (channel < 1) or (channel > self._nchannels):
			raise ValueError("Channel {} is out of range (valid channel range is 1 to {})".format(channel, self._nchannels))
		if not isinstance(enable, bool):
			raise ValueError("Enable flag has to be True or False")
		if not self._capabilities['onoff']:
			raise TypeError("This device does not support on/off switching")

		return self._setChannelEnable(enable, channel)

	def setVoltage(self, voltage, channel = 1):
		if not isinstance(channel, int):
			raise ValueError("Channel has to be an integer number")
		if (channel < 1) or (channel > self._nchannels):
			raise ValueError("Channel {} is out of range (valid channel range is 1 to {})".format(channel, self._nchannels))
		if not (isinstance(voltage, float) or isinstance(voltage, int)):
			raise ValueError("Voltage has to be an integer in range {} to {}".format(vrange[0], vrange[1]))

		pTarget = abs(voltage * self._setValues[channel-1]['amps'])
		if (pTarget < self._prange[0]) or (pTarget > self._prange[1]):
			raise ValueError("Selected voltage lies out of supported power range ({} to {} watts)".format(self._prange[0], self._prange[1]))

		if self._setVoltage(voltage, channel):
			self._setValues[channel-1]['volts'] = voltage

	def setCurrent(self, current, channel = 1):
		if not isinstance(channel, int):
			raise ValueError("Channel has to be an integer number")
		if (channel < 1) or (channel > self._nchannels):
			raise ValueError("Channel {} is out of range (valid channel range is 1 to {})".format(channel, self._nchannels))
		if not (isinstance(current, float) or isinstance(current, int)):
			raise ValueError("Current has to be an integer in range {} to {}".format(arange[0], arange[1]))

		pTarget = abs(current * self._setValues[channel-1]['volts'])
		if (pTarget < self._prange[0]) or (pTarget > self._prange[1]):
			raise ValueError("Selected current lies out of supported power range ({} to {} watts)".format(self._prange[0], self._prange[1]))

		if self._setCurrent(current, channel):
			self._setValues[channel-1]['amps'] = current

	def getVoltage(self, channel = 1):
		if not isinstance(channel, int):
			raise ValueError("Channel has to be an integer number")
		if (channel < 1) or (channel > self._nchannels):
			raise ValueError("Channel {} is out of range (valid channel range is 1 to {})".format(channel, self._nchannels))

		measVolts = None
		if self._capabilities['measureV']:
			measVolts = self._getVoltage(channel)

		return measVolts, self._setValues[channel-1]['volts']

	def getCurrent(self, channel = 1):
		if not isinstance(channel, int):
			raise ValueError("Channel has to be an integer number")
		if (channel < 1) or (channel > self._nchannels):
			raise ValueError("Channel {} is out of range (valid channel range is 1 to {})".format(channel, self._nchannels))

		measCurrent = None
		if self._capabilities['measureA']:
			measCurrent = self._getCurrent(channel)

		return measCurrent, self._setValues[channel-1]['amps']

	def off(self):
		return self._off()

	def getLimitMode(self, channel = 1):
		if not isinstance(channel, int):
			raise ValueError("Channel has to be an integer number")
		if (channel < 1) or (channel > self._nchannels):
			raise ValueError("Channel {} is out of range (valid channel range is 1 to {})".format(channel, self._nchannels))

		return self._getLimitMode(channel)

	# Imperative connect & disconnect methods

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
