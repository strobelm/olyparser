#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""Olympiapark Munich Event to icalendar parser.

This program fetches the events taking place in Olympiapark in Munich
and converts them to an ical file which can be read by e.g. Thunderbird.

The output will be written to 'cal_olypark.ics' in the current directory.

One may wants to adjust the 'url' variable below, currently it lists the
events of 2017.
"""

import os
import icalendar as ical
import re
import urllib.request
import dateutil.parser
from bs4 import BeautifulSoup

from event import Event

__author__ = "Michael Strobel"
__license__ = "GPL v3"
__version__ = "0.1"
__email__ = "strobel AT ma DOT tum DOT de"

# Fetch Events from Olympiapark.de
# This is 2017
url = """
http://www.olympiapark.de/de/no_cache/veranstaltungen-tickets/uebersicht/?tx_event_pi4%5Bstart%5D=1483225200&tx_event_pi4%5Bstop%5D=1514761200&tx_event_pi5%5Bm%5D=1483225200
""" # noqa 

# Some locations are ignored because they don't attract much audience
# alter to your needs
ignored_locations = ["Rockmuseum", "Liegewiese"]

#
# from here on no adjustments should be necessary
#
duparse = dateutil.parser.parse

raw_html = urllib.request.urlopen(url).read().decode("utf-8")
soup = BeautifulSoup(raw_html, 'html.parser')

# Events occur in even and odd class (used for CSS highlighting)
divodd = soup.find_all("div", class_="item odd")
diveven = soup.find_all("div", class_="item even")
divs = divodd + diveven

# olyevents accumulates the events for later processing
olyevents = []
for it in divs:
    date = it.find("div", class_="date")
    name = it.find("div", class_="event")
    location = it.find("div", class_="location")
    # hour does unfortunately posses no own class
    hour = location.find_next_sibling()

    if location.text not in ignored_locations:
        olyevents.append(Event(date.text, hour.text, location.text, name.text))

# write to ical
cal = ical.Calendar()

# match time formats like 16:35 - 17:50
timef = """([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]\s*\
        -\s*([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]"""
reg = re.compile(timef)
for it in olyevents:
    ev = ical.Event()
    # split dates like 01.01.2017 - 03.01.2017
    pdate = it.date.split(" - ")
    start = duparse(pdate[0], dayfirst=True)

    # The timing format is not unique - just handle the case of HH:MM - HH:MM
    # otherwise we will create an all day event
    htmp = it.hour
    htmp = re.search(reg,  htmp)
    if htmp:
        # group(0) - just take the first occurrence
        htmp = htmp.group(0).split(" - ")
        s0 = duparse(htmp[0], dayfirst=True)
        start = start.replace(hour=s0.hour, minute=s0.minute)
    # default all day event
    else:
        startback = start
        start = start.date()

    ev.add('dtstart', start)

    # do we have an end?
    if len(pdate) > 1:
        end = duparse(pdate[-1], dayfirst=True)
        # workaround for different time formats
        if type(start) is type(end):
            delta = (end - start).days
        else:
            delta = (end - startback).days
        # multiple days
        # only add events if its reasonable
        if delta > 0 and delta < 3:
            # if we got HH:MM then replace
            if htmp:
                s1 = duparse(htmp[1], dayfirst=True)
                end = end.replace(hour=s1.hour, minute=s1.minute)
            ev.add('dtend', end)

    # add summary location etc
    ev.add('summary', it.name)
    ev.add('location', it.location)
    cal.add_component(ev)


# write out cal file
directory = os.path.dirname(os.path.realpath(__file__))
f = open(os.path.join(directory, 'cal_olypark.ics'), 'wb')
f.write(cal.to_ical())
f.close()
