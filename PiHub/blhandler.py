import subprocess, re, time, os, threading, binascii

from codecs import encode, decode
from bluepy import btle
from collections import namedtuple

ADDR_TYPE_PUBLIC = "public"
ADDR_TYPE_RANDOM = "random"

ISIT_SERVICE 	= 'bd330659-97ce-5163-c30d-b14495294580'
ISIT_CHAR		= 'cdd772fd-dd62-4cee-a2fa-d76dbee2045d'

SIGINT = 2

if os.getuid() != 0:
        print("You need to run this as root.")
        raise Exception('Not elevated to root')

Sensor = namedtuple("Sensor", "con service char mutex")
debugging = False

def DBG(*args):
	if debugging:
		print(''.join([str(a) for a in args]))

class SensorHandler():
	
	__iface = None
	__localMac = None

	__connectedSensors = {}
	__connectedSensorsMutex = threading.Lock()
	faultySensors = {}
	
	__sensorStates = {}
	__stateListMutex = threading.Lock()
	
	__scanner = None
	__scanThread = None

	__notificationThread = None

	def __init__(self, iface=0, serviceUUID=ISIT_SERVICE, characterUUID=ISIT_CHAR):
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

		self.serviceUUID = serviceUUID
		self.characterUUID = characterUUID

		self.__initializeDevice()
		self.__initializeScanner()
		self.__notificationThread = threading.Thread(target=self.__checkNotifications, daemon=True)
		self.__notificationThread.start()

	def handleNotification(self, cHandle, data):
		DBG("Notification:", cHandle, "sent data", binascii.b2a_hex(data))

	def handleDiscovery(self, scanEntry, isNewDev, isNewData):
		if isNewDev and self.__checkIfValidScanEntry(scanEntry):
			self.__connect(scanEntry)

	def __processScanner(self):
		while True:
			try:
				if not self.__scanner.helperRunning():
					self.__scanner.start()

				self.__scanner.process(None)
			except Exception as e:
				DBG('Exception while processing scanner. Error {0}'.format(e))
				time.sleep(3)
			time.sleep(2)

	def __checkNotifications(self):
		while True:
			connectedSensors = []
			with self.__connectedSensorsMutex:
				connectedSensors = list(self.__connectedSensors.items())
			for addr, sensor in connectedSensors:
				try:
					with sensor.mutex:
						if not sensor.con.helperRunning():
							sensor.con.reconnect()

						sensor.con.waitForNotifications(0.1)
				except Exception as e:
					DBG('Exception while checking for notification. Error {0}'.format(e))
					time.sleep(3)
			
			time.sleep(2)
				

	def __connect(self, scanEntry):
		try:
			sensorCon = Peripheral(scanEntry)
			sensorService = sensorCon.getServiceByUUID(self.serviceUUID)
			sensorChar = sensorService.getCharacteristics(self.characterUUID)[0]
			sensorCon.withDelegate(self)
			with self.__connectedSensorsMutex:
				self.__connectedSensors[sensorCon.deviceAddr] = Sensor(con=sensorCon, service=sensorService, char=sensorChar, mutex=threading.Lock())
		except btle.BTLEException as e:
			DBG('Unable to connect to {0} with error {1}'.format(scanEntry.addr, e))

	def __checkIfValidScanEntry(self, scanEntry):
		with self.__connectedSensorsMutex:
			if scanEntry.addr in self.__connectedSensors:
				return False

		longuuidservice = scanEntry.getValueText(7)
		longuuidservice = scanEntry.getValueText(6) if longuuidservice is None else longuuidservice
		if longuuidservice is None:
			return False
		longuuidservice = encode(decode(longuuidservice, 'hex')[::-1], 'hex').decode()
		uuid = btle.UUID(longuuidservice)
		if uuid != self.serviceUUID:
			return False
		return True

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
	

	def getSensorStates(self):
		self.tryReconnect()
		states = {}
		sensors = {}
		with self.__connectedSensorsMutex:
			sensors = list(self.__connectedSensors.items())
		for addr, sensor in sensors:
			try:
				states[addr] = int.from_bytes(self.getSensorState(sensor), byteorder='little')
			except (btle.BTLEException, BrokenPipeError) as e:
				try:
					with sensor.mutex:
						sensor.con.reconnect()
					states[addr] = int.from_bytes(self.getSensorState(sensor), byteorder='little')
				except Exception as e:
					self.faultySensors[addr] = e
					with self.__connectedSensorsMutex:
						del self.__connectedSensors[addr]

		return states

	def tryReconnect(self):
		faultySensors = list(self.faultySensors.items())
		for addr, sensor in faultySensors:
			try:
				with sensor.mutex:
					sensor.con.reconnect()
				with self.__connectedSensorsMutex:
					self.__connectedSensors[addr] = sensor
				del self.faultySensors[addr]
			except Exception as e:
				pass

	def getAvaliableSensors(self):
		with self.__connectedSensorsMutex:
			return list(self.__connectedSensors.keys())

	def close(self):
		self.__scanThread.exit()
		self.__notificationThread.exit()
		for addr, sensor in self.__connectedSensors.items():
			try:
				sensor.disconnect()
			except (btle.BTLEException, BrokenPipeError) as e:
				pass

	def getSensorState(self, sensor):
		with sensor.mutex:
			return sensor.char.read()

class Peripheral(btle.Peripheral):

	def __init__(self, deviceAddr=None, addrType=ADDR_TYPE_PUBLIC, iface=None):
		btle.Peripheral.__init__(self, deviceAddr, addrType, iface)

	def helperRunning(self):
		return self._helper is not None and self._helper.poll() is None

	def reconnect(self):
		if not self.helperRunning():
			self._helper = None
			self.connect(self.deviceAddr, self.addrType, self.iface)

class Scanner(btle.Scanner):
	def __init__(self, iface=0):
		btle.Scanner.__init__(self, iface)

	def helperRunning(self):
		return self._helper is not None and self._helper.poll() is None