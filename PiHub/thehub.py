import argparse, sys, threading, time, signal, os, traceback
from hubsettings import HubSettings
from apihandler import APIHandler

class TheHub:

    __api = None
    __settings = None
    __updateRate = 0
    __mutex = None

    def __init__(self, settingsFile, updateRate = 5):
        self.__settings = HubSettings(settingsFile)
        self.__api = APIHandler(self.__settings.APIUrl)
        self.__updateRate = updateRate
        self.__mutex = threading.Lock()

    def Run(self):
        #print(self.__settings.Room)
        thread = threading.Thread(target=self.InputParser, daemon=True)
        thread.start()
        while True:
            time.sleep(self.__updateRate)
            self.__mutex.acquire()
            # Check bluetooth devices and update the API
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
                elif command == 'update':
                    self.__settings.Update()
                elif command == 'delete':
                    self.Delete(commands.pop(0), commands.pop(0))
                elif command == 'testdevice':
                    bleMAC = commands.pop(0)
                    # Test a device and get its information
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

    def List(self, whatToList):
        if whatToList == 'devices':
            pass
        elif whatToList == 'seats':
            for key, value in self.__settings.Room['seats'].items():
                print(key+":", value)
        elif whatToList == 'links':
            for key, value in self.__settings.Bluetooth.items():
                print(key+":", value)
        else:
            print('{0} cannot be listed.'.format(whatToList))

    def Delete(self, whatToDelete, name):
        if whatToDelete == 'seat':
            self.__api.DeleteSeat(name)
            self.__settings.Update()
        elif whatToDelete == 'link':
            del self.__settings.Bluetooth[name]
        else:
            print('{0} cannot be deleted.'.format(whatToDelete))

    def New(self, commands):
        whatToAdd = commands.pop(0)
        if whatToAdd == 'seat':
            seatName = commands.pop(0)
            seatID = self.__api.CreateSeat(self.__settings.Room['ID'], seatName)
            if seatID is not None:
                self.__settings.Update()
                print('Added a new seat to the room with name {0} and ID {1}.'.format(seatName, seatID))
            else:
                print('There was an error when adding seat.')
        elif whatToAdd == 'link':
            seatID = commands.pop(0)
            bleMAC = commands.pop(0)
            print('{0},{1}'.format(bleMAC, seatID))
        else:
            print('{0} cannot be deleted.'.format(whatToAdd))

    def PrintCommandHelp(self):
        print("""new \n\tseat <seatName>\n\tlink <seatID> <bleMAC>
list \n\tdevices\n\tseats\n\tlinks
update
delete \n\tseat <seatID>\n\tlink <bleMAC>
testdevice <bleMAC>
help
quit""")


def signal_handler(signal, frame):
    print('You pressed Ctrl+C')
    os._exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', help='Path to settings file', type=str, metavar='<path>')
    args = parser.parse_args()
    hub = TheHub(args.s)
    hub.Run()
