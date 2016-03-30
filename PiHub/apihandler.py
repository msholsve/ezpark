import requests,json

class APIHandler():

    __apiUrl = ''

    def __init__(self, APIUrl):
        self.__apiUrl = APIUrl if APIUrl.startswith('http://') else 'http://' + APIUrl
        self.__apiUrl = self.__apiUrl if self.__apiUrl.endswith('/') else self.__apiUrl + '/'
        req = requests.get(self.__apiUrl)
        if not self.__checkRequest(req, 200, "The givene API address is invalid or unavaliable."):
            raise Exception(" The givene API address is invalid or unavaliable")

    def GetRooms(self):
        req = requests.get(self.__apiUrl+'rooms')
        if not self.__checkRequest(req, 200, "Unable to get rooms."):
            return None
        rooms = {}
        for room in req.json()['_items']:
            rooms[room['_id']] = room['name']
        return rooms

    def GetRoom(self, roomID):
        req = requests.get(self.__apiUrl+'rooms/' + roomID + '?projection={"map":%200}')
        if not self.__checkRequest(req, 200, "Unable to get the room."):
            return None
        roomJson = req.json()
        room = {'name': roomJson['name'], 'ID': roomJson['_id']}
        if 'seats' not in roomJson:
            return room
        seats = {}
        for seat in roomJson['seats']:
            seats[seat['_id']] = seat['name']
        room['seats'] = seats
        return room

    def CreateRoom(self, roomName):
        req = requests.post(self.__apiUrl+'rooms', json={'name':roomName})
        return self.__checkRequest(req, 201, "Unable to create room.")

    def CreateSeat(self, roomID, seatName):
        req = requests.post(self.__apiUrl+'seats', json={'name':seatName})
        if not self.__checkRequest(req, 201, "Unable to create seat."):
            return None
        room = self.GetRoom(roomID)
        if room is None:
            return None
        seats = list(room['seats'].keys()) if 'seats' in room else []
        seats.append(req.json()['_id'])
        return req.json()['_id'] if self.SetSeatsOnRoom(room['ID'], seats) else None

    def GetAllSeats(self):
        req = requests.get(self.__apiUrl+'seats')
        if not self.__checkRequest(req, 200, 'Unable to get all seats.'):
            return None
        seats = {}
        for seat in req.json()['_items']:
            free = None;
            if 'free' in seat:
                free = seat['free']
            seats[seat['_id']] = {'free': free, 'name': seat['name']}
        return seats

    def SeatExists(self, seatID):
        req = requests.get(self.__apiUrl+'seats/'+seatID)
        return req.status_code == 200

    def SetSeatsOnRoom(self, roomID, seats):
        req = requests.patch(self.__apiUrl+'rooms/'+roomID, json={'seats':seats})
        return self.__checkRequest(req, 200, "Unable to update seats.")

    def ChangeSeatState(self, seatID, state):
        req = requests.patch(self.__apiUrl+'seats/'+seatID, json={'free':state})
        return self.__checkRequest(req, 200, "Unable to update seat state.")

    def GetSeatState(self, seatID):
        req = requests.get(self.__apiUrl+'seats/'+seatID)
        if not self.__checkRequest(req, 200, "Unable to update seat state."):
            return False
        free = None;
        if 'free' in req.json():
            free = req.json()['free']
        return free

    def DeleteSeat(self, seatID):
        req = requests.delete(self.__apiUrl+'seats/'+seatID)
        return self.__checkRequest(req, 204, "Unable to delete seat.")

    def __checkRequest(self, request, expectedCode, errorMessage):
        if request.status_code == expectedCode:
            return True
        print(errorMessage+'\n\tStatus code:{0}'.format(request.status_code), request.url+'\n', request.content)
        return False

if __name__ == "__main__":
    api = APIHandler('http://isit.routable.org/api')
    rooms = api.GetRooms()
    print('Rooms:',rooms)
    for roomID, roomName in rooms.items():
        print(roomName,api.GetRoom(roomID),'\n')

