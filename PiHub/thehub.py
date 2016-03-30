import os
if os.getuid() != 0:
        print("You need to run this as root.")
        os._exit(1)
import argparse, sys, threading, time, signal, traceback, blhandler
from hubsettings import HubSettings
from apihandler import APIHandler
from blhandler import SensorHandler

debug = False

class TheHub:

    __api = None
    __settings = None
    __updateRate = 0
    __mutex = None
    __pollSensors = True

    def __init__(self, settingsFile, polling, updateRate = 5):
        blhandler.debugging = debug
        self.__settings = HubSettings(settingsFile)
        self.__api = APIHandler(self.__settings.APIUrl)
        self.__sensors = SensorHandler()
        self.__updateRate = updateRate
        self.__mutex = threading.Lock()
        self.__pollSensors = polling

    def Run(self):
        #print(self.__settings.Room)
        thread = threading.Thread(target=self.InputParser, daemon=True)
        thread.start()
        while True:
            time.sleep(self.__updateRate)
            self.__mutex.acquire()
            if not self.__pollSensors:
                self.__mutex.release()
                continue
            states = self.__sensors.getSensorStates()
            for mac, state in states.items():
                if mac in self.__settings.Bluetooth:
                    self.__api.ChangeSeatState(self.__settings.Bluetooth[mac], state > 0)
            self.__mutex.release()

    def InputParser(self):
        while True:
            print('# ', end='', flush=True)
            inputString = sys.stdin.readline()
            self.__mutex.acquire()
            self.ExecuteCommand(inputString.split())
            self.__mutex.release()

    def ExecuteCommand(self, commands):
        try:
            while len(commands) > 0:
                command = commands.pop(0)
                if   command == 'new':
                    self.New(commands)
                elif command == 'list':
                    self.List(commands.pop(0))
                elif command == 'set':
                    self.Set(commands)
                elif command == 'update':
                    self.__settings.Update()
                elif command == 'delete':
                    self.Delete(commands.pop(0), commands.pop(0))
                elif command == 'statues':
                    bleMAC = commands.pop(0)
                    # Test a device and get its information
                elif command == 'info':
                    
                    pass
                elif command == 'help':
                    self.PrintCommandHelp()
                elif command == 'quit':
                    os._exit(0)
                else:
                    print('{0} is not a valid command.'.format(command))

                self.__settings.Save()
        except Exception as e:
            print('Error while executing command.', e)
            traceback.print_exc()

    def New(self, commands):
        whatToAdd = commands.pop(0)
        if whatToAdd == 'seat':
            seatName = commands.pop(0)
            if self.__api.SeatExists(seatName):
                newSeatSet = list(self.__settings.Room['seats'].keys())
                newSeatSet.append(seatName)
                if self.__api.SetSeatsOnRoom(self.__settings.Room['ID'], newSeatSet):
                    print('Seat {0} was added to the room.'.format(seatName, seatID))
                    return self.__settings.Update()
            seatID = self.__api.CreateSeat(self.__settings.Room['ID'], seatName)
            if seatID is not None:
                self.__settings.Update()
                print('Added a new seat to the room with name {0} and ID {1}.'.format(seatName, seatID))
            else:
                print('There was an error when adding seat.')

        elif whatToAdd == 'link':
            seatID = commands.pop(0)
            bleMAC = commands.pop(0)
            self.__settings.Bluetooth[bleMAC] = seatID;
            print('Link added: {0}=>{1}'.format(bleMAC, seatID))
        else:
            print('{0} cannot be added.'.format(whatToAdd))

    def List(self, whatToList):
        dictionary = {}
        if whatToList == 'sensors':
            dictionary = self.__sensors.getSensorStates()
        elif whatToList == 'seats':
            for seatID, name in self.__settings.Room['seats'].items():
                dictionary[seatID] = {'free': self.__api.GetSeatState(seatID), 'name': name}
        elif whatToList == 'allseats':
            dictionary = self.__api.GetAllSeats()
        elif whatToList == 'links':
            dictionary = self.__settings.Bluetooth
        else:
            print('{0} cannot be listed.'.format(whatToList))
            return
        if dictionary is not None:
            for key, value in sorted(dictionary.items()):
                print(key+": ", end='')
                if isinstance(value, dict):
                    for paramName, paramValue in sorted(value.items()):
                        print(paramName+':', paramValue, end='\t')
                    print()
                else:
                    print(value)

    def Set(self,commands):
        command = commands.pop(0)
        if command == 'seatstate':
            self.SetSeatState(commands.pop(0), commands.pop(0))
        if command == 'sensorpolling':
            newState = commands.pop(0)
            self.__pollSensors = self.__parseTextBool(newState,'enabled', 'disabled', 'Invalid polling state.')
            print('Sensor polling {0}.'.format(newState))
        pass

    def Delete(self, whatToDelete, name):
        if whatToDelete == 'seat':
            self.__api.DeleteSeat(name)
            self.__settings.Update()
        elif whatToDelete == 'link':
            del self.__settings.Bluetooth[name]
        else:
            print('{0} cannot be deleted.'.format(whatToDelete))

    def SetSeatState(self, seatID, state):
        state = self.__parseTextBool(state, 'free', 'occupied', 'Invalid seat state.')
        print(state)
        if seatID in self.__settings.Room['seats']:
            self.__api.ChangeSeatState(seatID, state)

    def __parseTextBool(self, text, trueText, falseText, errorMessage):
        if text.lower() == trueText.lower():
            return True
        elif text.lower() == falseText.lower():
            return False
        else:
            raise Exception(errorMessage)


    def PrintCommandHelp(self):
        print("""new \n\tseat <new seatName/existing seatID>\n\tlink <seatID> <bleMAC>
list \n\tdevices\n\tseats\n\tallseats\n\tlinks
set\n\tseatstate\tfree/occupied\n\tsensorpolling\tenabled/disabled
update
delete \n\tseat <seatID>\n\tlink <bleMAC>
testdevice <bleMAC>
info
help
quit""")


def signal_handler(signal, frame):
    print('You pressed Ctrl+C')
    os._exit(0)

if __name__ == "__main__":
    #signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', help='Path to settings file', type=str, metavar='<path>')
    parser.add_argument('-p', help='Start polling', default=True)
    parser.add_argument('-d', help='Enable debug output', action='store_true')
    args = parser.parse_args()
    debug = args.d
    hub = TheHub(args.s, args.p)
    hub.Run()
