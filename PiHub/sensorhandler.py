import subprocess, re, time, os, threading, binascii, traceback

from codecs import encode, decode
from bluepy import btle
from collections import namedtuple

ISIT_SERVICE_128 	= 'bd330659-97ce-5163-c30d-b14495294580'
ISIT_SERVICE_16		= '0659'

if os.getuid() != 0:
        print("You need to run this as root.")
        raise Exception('Not elevated to root')

debugging = False

def DBG(*args):
	if debugging:
		print(''.join([str(a) for a in args]))

class SensorHandler():
	
	__iface = None
	__localMac = None
	
	__sensorStates = {}

	SensorDataHandler = None
	
	__scan = True
	__scanner = None
	__scanThread = None

	def __init__(self, iface=0):
		localDevices = self.__getLocalDevices()
		btle.Debugging = debugging

		if not len(localDevices) > 0:
			raise EnvironmentError('No avaliable devices.')

		if iface in localDevices:
			self.__iface = iface
			self.__localMac = localDevices[iface]
		else:
			dev = list(localDevices.items())[0]
			self.__iface = dev[0]
			self.__localMac = dev[1]
			print('Preffered iface {0} was not avaliable, iface {1} was selected.'.format(iface, self.__iface))

		self.shortUUID = btle.UUID(ISIT_SERVICE_16)
		self.longUUID = btle.UUID(ISIT_SERVICE_128)

		self.__initializeDevice()
		self.__initializeScanner()

	def handleNotification(self, cHandle, data):
		DBG("Notification:", cHandle, "sent data", binascii.b2a_hex(data))

	def handleDiscovery(self, scanEntry, isNewDev, isNewData):
		DBG("New discovery:", scanEntry.getScanData())
		data = self.__parseScanEntry(scanEntry)
		if (isNewDev or isNewData) and data is not None:
			self.__sensorStates[scanEntry.addr] = data
			if self.SensorDataHandler is not None:
				self.SensorDataHandler(scanEntry.addr, data)

	def __processScanner(self):
		while self.__scan:
			try:
				if not self.__scanner.helperRunning():
					self.__scanner.start()

				self.__scanner.process(None)
			except Exception as e:
				DBG('Exception while processing scanner. Error {0}'.format(e), traceback.format_exc())
			time.sleep(2)

	def __parseScanEntry(self, scanEntry):
		data = None
		uuid = None
		longuuidServiceData = scanEntry.getValueText(0x21)
		shortuuidServiceData = scanEntry.getValueText(0x16)
		if longuuidServiceData != None:
			uuid = btle.UUID(encode(decode(longuuidServiceData[0:32], 'hex')[::-1], 'hex').decode())
			if uuid == self.longUUID:
				data = longuuidServiceData[32:len(longuuidServiceData)]
		elif shortuuidServiceData != None:
			uuid = btle.UUID(encode(decode(shortuuidServiceData[0:4], 'hex')[::-1], 'hex').decode())
			if uuid == self.shortUUID:
				data = shortuuidServiceData[4:len(shortuuidServiceData)]
		return data

	def __getLocalDevices(self):
		output = subprocess.check_output(['hcitool', 'dev'])
		matches = re.findall(r'\\thci([0-9]+)\\t((?:[A-Fa-f0-9]+:){5}[A-Fa-f0-9]+)\\n', str(output), re.MULTILINE)
		return dict([(int(match[0]), match[1]) for match in matches])

	def __initializeDevice(self):
		device = 'hci'+str(self.__iface)
		output = subprocess.check_output(['hciconfig', device, 'down'])
		output = subprocess.check_output(['hciconfig', device, 'up'])

	def __initializeScanner(self):
		self.__scanner = Scanner(self.__iface)
		self.__scanner.withDelegate(self)
		self.__scanner.start()
		self.__scanThread = threading.Thread(target=self.__processScanner, daemon=True)
		self.__scanThread.start()

	def getAvaliableSensors(self):
		return self.__sensorStates

	def close(self):
		self.__scan = False
		self.__scanThread.join()

class Scanner(btle.Scanner):
	def __init__(self, iface=0):
		btle.Scanner.__init__(self, iface)

	def helperRunning(self):
		return self._helper is not None and self._helper.poll() is None