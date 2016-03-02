#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import requests
from pprint import pprint
import sys
import base64
import StringIO
import json

BASEURL = "http://isit.routable.org/api"
TO_BE_PLACED = []

CURRENTLY_PLACING = None


def get_rooms():
    r = requests.get(BASEURL + '/rooms')
    return r.json()['_items']


def get_room(idyo):
    r = requests.get(BASEURL + '/rooms/' + idyo)
    return r.json()

def set_title(title):
    fig.canvas.set_window_title(title)


rooms = get_rooms()
for i, room in enumerate(rooms):
    print("{:2d} - {}".format(i, room['name']))
chosen = int(raw_input('Choose room:'))

room = get_room(rooms[chosen]['_id'])

if 'map' not in room:
    print 'No map : (\nYou should upload one!'
    print 'Use the following command:'
    print 'curl --request PATCH -F "map=@FILENAME" {}/rooms/{}'.format(BASEURL, room['_id'])
    sys.exit(0)
print 'There are {} seats!'.format(len(room['seats']))
print '-'*20
for seat in room['seats']:
    if 'location' in seat:
        print('{:16} - {:3}, {:3}'.format(seat['name'], seat['location']['x'], seat['location']['y']))
    else:
        print('{:16} - Unplaced!'.format(seat['name']))
print '-'*20
place_all = raw_input('Place [all] or only unplaced(default)? ') in ['all', 'All', 'A', 'a']
for seat in room['seats']:
    if 'location' in seat and not place_all:
        continue
    TO_BE_PLACED.append((seat['name'], seat['_id']))


imgdata = base64.b64decode(room['map']['file'])
imagetype = room['map']['name'].split('.')[-1]
im = mpimg.imread(StringIO.StringIO(imgdata), imagetype)
ax = plt.gca()
fig = plt.gcf()
implot = ax.imshow(im)

CURRENTLY_PLACING = TO_BE_PLACED.pop(0)
set_title(CURRENTLY_PLACING[0])

def update_position(_id, x, y):
    headers = {'Content-Type': 'application/json'}
    data = {'location': {'x':int(x), 'y':int(y)}}
    r = requests.patch(BASEURL + '/seats/' + _id, headers=headers, data=json.dumps(data))
    if r.status_code == 200:
        print 'Updated position of {}'.format(CURRENTLY_PLACING[0])
    else:
        print r.json()

def onclick(event):
    global CURRENTLY_PLACING
    if event.xdata != None and event.ydata != None:
        #print(event.xdata, event.ydata)
        update_position(CURRENTLY_PLACING[1], event.xdata, event.ydata)
        if len(TO_BE_PLACED) != 0:
            CURRENTLY_PLACING = TO_BE_PLACED.pop(0)
            set_title(CURRENTLY_PLACING[0])
        else:
            plt.close()

cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()
