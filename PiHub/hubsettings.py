import json
import apihandler
import requests

class HubSettings():

    __file = 'hub.settings'

    def __init__(self, fileName=None):
        if fileName != None:
            self.__file = fileName

        settingsRead = self.__readSettings()
        isValid = self.__checkValidSettings()
        if not settingsRead:
            self.__applyDict(self.__setupDefaultSettings())
        elif isValid is not None:
            print(isValid)
            yesNo = input('Settings file is not correct, do you want to run the setup?[y/n]')
            if yesNo is not 'y':
                print('Unable to continue without a valid settings file, please fix the settings file and restart.')
                raise Exception("No valid settings file")
            self.__applyDict(self.__setupDefaultSettings())
        else:
            self.Update()

        self.__saveSettings()

    def Save(self):
        isItValid = self.__checkValidSettings()
        if isItValid is not None:
            print('Invalid settings, unable to save settings.')
            return
        self.__saveSettings()

    def Update(self):
        api = apihandler.APIHandler(self.APIUrl)
        room = api.GetRoom(self.Room['ID'])
        if room is not None:
            self.Room = room

    def __getitem__(self, key):
        if (isinstance(key,str) or isinstance(key, unicode)) and key in self.__dict__:
            return self.__dict__[key]

    def __applyDict(self, settings):
        for key, value in settings.items():
            self.__dict__[key] = value

    def __readSettings(self):
        try:
            with open(self.__file, 'r') as f:
                settingsString = f.read()
                self.__applyDict(json.loads(settingsString))
            return True
        except:
            return False

    def __saveSettings(self):
        settings = dict(self.__dict__)
        if '_HubSettings__file' in settings:
            del settings['_HubSettings__file']
        try:
            with open(self.__file, 'w') as f:
                settingsString = json.dumps(settings, sort_keys = True, indent = 4)
                f.write(settingsString)
            return True
        except:
            return False

    def __checkValidSettings(self):
        if not all (key in self.__dict__ for key in ['APIUrl', 'Bluetooth', 'Room']):
            return self.__invalidSettingStringGen('Root', ['APIUrl', 'Bluetooth', 'Room'])
        if not isinstance(self.__dict__['Room'], dict):
            return 'Room is not a dictionary'
        if not all (key in self.__dict__['Room'] for key in ['ID', 'name', 'seats']):
            return self.__invalidSettingStringGen('Room', ['ID', 'name', 'seats'])
        return None

    def __invalidSettingStringGen(self, level, requiredKeys):
        return '{0} level should contain {1}'.format(level, requiredKeys)

    def __setupDefaultSettings(self, APIUrl = None, Room = None):
        if APIUrl is None:
            APIUrl = input('API url:')
        api = apihandler.APIHandler(APIUrl)

        if Room is None:
            Room = input('Room name/ID:')
        room = api.GetRoom(Room)
        if room is None:
            yesNo = input('Room does not exist, do you want to create the room? [y/n]:')
            if yesNo is not 'y':
                return self.__setupDefaultSettings(APIUrl)
            if api.CreateRoom(room):
                return self.__setupDefaultSettings(APIUrl, post.json()['_id'])

        return {'APIUrl': APIUrl, 'Room': room, 'Bluetooth': {}}

if __name__ == "__main__":
    settings = HubSettings()
    print(settings.Room)
    print(settings['Room'])
