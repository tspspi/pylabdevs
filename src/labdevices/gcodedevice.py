import atexit

from enum import Enum

class GCodeDevice:
	def __init__(
		self,

		name = "GCODEDEVICE",

		supportedGCodes = [ ],
		usesThread = False,

		echoConsole = False,
		hasEndstops = True,

		useMetric = True,
		useAbsolute = True
	):
		self._name = name

		self._usesContext = False
		self._usedConnect = False

		self._supported_gcodes = supportedGCodes
		self._hasEndstops = hasEndstops

		self._echo_console = False

		self._cb_echo = None

		self._use_metric = useMetric
		self._use_absolute = useAbsolute

	# Overriden methods

	def _cmd_getEndstopState(self, sync = False):
		raise NotImplementedError("Getting endstop state is currently not implemented")
	def _cmd_set_metric(self, sync = True):
		raise NotImplementedError("Setting metric units is currently not implemented")
	def _cmd_set_imperial(self, sync = True):
		raise NotImplementedError("Setting imperial units is currently not implemented")
	def _cmd_set_absolute(self, sync = True):
		raise NotImplementedError("Setting absolut positioning is currently not implemented")
	def _cmd_set_relative(self, sync = True):
		raise NotImplementedError("Setting relative positioning is currently not implemented")
	def _cmd_move(self, X = None, Y = None, Z = None, feedrate = None, sync = False, travelOnly = False):
		raise NotImplementedError("Linear movement not implemented")
	def _cmd_home(self, homeXY = True, homeZ = True, sync = True):
		raise NotImplementedError("Homing not implemented")
	def _cmd_disable_steppers(self, X = True, Y = True, Z = True, sync = True):
		raise NotImplementedError("Disabling steppers not implemented")

	# Exposed API:
	def get_endstops(self, sync = False):
		if self._hasEndstops:
			return self._cmd_getEndstopState(sync = sync)
		else:
			return { }

	def move(self, X = None, Y = None, Z = None, feedrate = None, sync = False, travelOnly = False):
		return self._cmd_move(X = X, Y = Y, Z = Z, feedrate = feedrate, sync = sync, travelOnly = travelOnly)

	def home(self, homeXY = True, homeZ = True, sync = False):
		return self._cmd_home(homeXY = homeXY, homeZ = homeZ, sync = sync)

	def positions_relative(self, sync = False):
		return self._cmd_set_relative(sync)

	def positions_absolute(self, sync = False):
		return self._cmd_set_absolute(sync)

	def set_metric(self, sync = True):
		return self._cmd_set_metric(sync)

	def set_imperial(self, sync = True):
		return self._cmd_set_imperial(sync)

	def disable_steppers(self, X = True, Y = True, Z = True, sync = True):
		return self._cmd_disable_steppers(X = X, Y = Y, Z = Z, sync = sync)

	# Event handling

	def _got_echo_message(self, msg):
		# We received an echo message that we might want to display on the console (depending on our configuration)
		if self._echo_console:
			print(f"[{self._name}] {msg}")

	# Imperative connection handling

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
			raise ValueError("Cannot use connect on a context managed object (with)")
		if not self._usedConnect:
			return True

		self._disconnect()
		self._usedConnect = False
		return True
