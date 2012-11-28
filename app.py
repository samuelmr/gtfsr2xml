#!/usr/bin/python

import gtfs_realtime_pb2
from flask import Flask
from urllib import urlopen
import time
import datetime
import os
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/predictions/<path:feed>')
def predictions(feed):
  gtfsrt = feed
  fm = gtfs_realtime_pb2.FeedMessage()
  feed = urlopen(gtfsrt)
  fm.ParseFromString(feed.read())
  timestamp = datetime.datetime.utcfromtimestamp(fm.header.timestamp)
  b = ET.Element('body')
  for entity in fm.entity:
    tu = entity.trip_update
    for stu in tu.stop_time_update:
      coll = ET.SubElement(b, 'predictions')
      coll.set('routeTag', tu.trip.trip_id)
      coll.set('routeTitle', tu.vehicle.label)
      coll.set('stopId', stu.stop_id)
      coll.set('stopSequence', stu.stop_sequence)
      dir = ET.SubElement(coll, 'direction')
      pred = ET.SubElement(dir, 'prediction')
      if (stu.departure.time):
        pred.set('epochTime', stu.arrival.time)
        pred.set('isDeparture', 'true')
      elif (stu.arrival.time):
        pred.set('epochTime', stu.arrival.time)
        pred.set('isDeparture', 'false')
  rv = app.make_response(ET.tostring(b))
  rv.mimetype = 'text/xml'
  return rv

@app.route('/vehicleLocations/<path:feed>')
def locations(feed):
  gtfsrt = feed
  fm = gtfs_realtime_pb2.FeedMessage()
  feed = urlopen(gtfsrt)
  fm.ParseFromString(feed.read())
  timestamp = datetime.datetime.utcfromtimestamp(fm.header.timestamp)
  b = ET.Element('body')
  for entity in fm.entity:
    ve = entity.vehicle
    pos = ve.position
    v = ET.SubElement(b, 'vehicle')
    v.set('id', ve.vehicle.id)
    v.set('routeTag', ve.trip.trip_id)
    v.set('lat', str(pos.latitude))
    v.set('lon', str(pos.longitude))
    v.set('heading', str(int(pos.bearing)))
    if (pos.speed):
      v.set('speedKmHr', str(pos.speed * 3.6))
  rv = app.make_response(ET.tostring(b))
  rv.mimetype = 'text/xml'
  return rv

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.debug = True
  app.run(host='0.0.0.0', port=port)
