#!/usr/bin/env python
import os
from eve import Eve
import json

here = os.path.dirname(__file__)


def before_returning_rooms(response):
    for room in response['_items']:
        room = before_returning_room(room)
        if 'seats' in room:
            del room['seats']
        if 'map' in room:
            del room['map']
    return response


def before_returning_room(room):
    free_seats = 0
    total_seats = 0
    if 'seats' in room and type(room['seats']) is list:
        free_seats = 0
        for seat in room['seats']:
            if type(seat) is dict:
                if 'free' in seat and seat['free']:
                    free_seats += 1
        room['seats'] = [seat for seat in room['seats'] if seat]
        total_seats = len(room['seats'])
    room['free_seats'] = free_seats
    room['total_seats'] = total_seats
    return room


app = Eve(settings=os.path.join(here, 'settings.py'))
app.on_fetched_resource_rooms += before_returning_rooms
app.on_fetched_item_rooms += before_returning_room


if __name__ == '__main__':
    app.run()
