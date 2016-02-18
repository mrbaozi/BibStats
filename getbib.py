#!/usr/local/bin/ python
# -*- coding: utf-8 -*-

import sys
import re
import json
from operator import add
from urllib.request import urlopen
from pylab import legend
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

if (len(sys.argv) < 3):
	nHours = 24
else:
	nHours = int(sys.argv[2])

nTicks = 7

############
##	FETCH
############

nVals = nHours * 12
url = 'http://seatfinder.bibliothek.kit.edu/karlsruhe/getdata.php'
jquery = '?callback=jQuery21408193237287923694_1439981931552'
location = '&location%5B0%5D=LSG%2CLST%2CLSW%2CLSM%2CLSN%2CLBS%2CFBC%2CLAF%2CFBW%2CFBM%2CFBP%2CFBI%2CFBA%2CBIB-N%2CFBH%2CFBD%2CTheaBib'
values = '&values%5B0%5D=seatestimate'
beforeAfter = '&after%5B0%5D=&before%5B0%5D=now'
limit = '&limit%5B0%5D=' + str(nVals)
source = urlopen(url + jquery + location + values + beforeAfter + limit).read()

############
##	DATA
############

# remove jQuery statement and whitespaces
data = json.loads(re.sub('\s\);|(\s+)(\w+)(\d+)_(\d+)\s\(\s', '', source.decode()))

# reading room IDs and verbose translation (for plot legend)
bibKeys = {'KITCS1':('LSG', 'LST', 'LSW', 'LSM', 'LSN', 'LBS'), \
		   'KITCS2':('FBC', 'LAF', 'FBW', 'FBM', 'FBP', 'FBI', 'FBA'), \
		   'KITCN':('BIB-N',), \
		   'HSK':('FBH',), \
		   'DHBW':('FBD',), \
		   'TheaBib':('TheaBib',)}

bibDetails = {'KITCS1':('Lesesaal Geisteswiss.', 'Lesesaal Technik', 'Lesesaal Wiwi & Info', 'Lesesaal Medienzentrum', 'Lesesaal Naturwiss.', 'Lehrbuchsammlung'), \
			'KITCS2':('Fachbibliothek Chemie', 'Lernzentrum Fasanenschl.', 'Fachbibliothek Wirtschaftswiss.', 'Fachbibliothek Mathematik', 'Fachbibliothek Physik', 'Fachbibliothek Informatik', 'Fachbibliothek Architektur'), \
			'KITCN':('KIT-Bibliothek Nord'), \
			'HSK':('Fachbibliothek Hochschule Karlsruhe'), \
			'DHBW':('Fachbibliothek DHBW Karlsruhe'), \
			'TheaBib':('TheaBib im Badischen Staatstheater')}

bibNames = {'KITCS1':u'Campus Süd (KIT-Bibliothek)', \
			'KITCS2':u'Campus Süd (Fachbibliotheken)', \
			'KITCN':u'KIT-Bibliothek Nord', \
			'HSK':u'Fachbibliothek Hochschule Karlsruhe', \
			'DHBW':u'Fachbibliothek DHBW Karlsruhe', \
			'TheaBib':u'TheaBib im Badischen Staatstheater'}

bibDetailsDict = {}
for key in bibKeys:
	bibDetailsDict.update({bibKeys[key][i]:bibDetails[key][i] for i in range(len(bibKeys[key]))})

############
##	PLOT
############

def plotOccupance(bibKey):
	# prepare data arrays
	plotDataOccupied = {key:[] for key in bibKeys[bibKey]}
	plotDataFree = {key:[] for key in bibKeys[bibKey]}
	timestamps = {key:[] for key in bibKeys[bibKey]}
	totalSeats = {key:[] for key in bibKeys[bibKey]}

	# extract json data to arrays
	totalOccupied = np.zeros(nVals)
	for key in bibKeys[bibKey]:
		tmpTotal = []
		for i in range(len(data[0]['seatestimate'][key])):
			tmpOccupied = data[0]['seatestimate'][key][i]['occupied_seats']
			tmpFree = data[0]['seatestimate'][key][i]['free_seats']
			tmpTotal.append(tmpOccupied)
			plotDataOccupied[key].append(tmpOccupied)
			plotDataFree[key].append(tmpFree)
			totalSeats[key] = (tmpFree+tmpOccupied)
			timestamps[key].append(data[0]['seatestimate'][key][i]['timestamp']['date'])
		totalOccupied += np.asarray(tmpTotal)

	for key in bibKeys[bibKey]:
		for i in range(len(timestamps[key])):
			timestamps[key][i] = re.sub('\s', '\n', timestamps[key][i])

	f, axarr = plt.subplots(2, sharex=True)

	for key in bibKeys[bibKey]:
		ticksX1 = [range(nVals)[i] for i in range(0, nVals, int(nVals/nTicks))]
		ticksX2 = [timestamps[key][range(nVals)[i]] for i in range(0, nVals, int(nVals/nTicks))]
		plt.xticks(ticksX1, ticksX2)
		axarr[1].plot(range(nVals), plotDataOccupied[key], label = bibDetailsDict[key] + u' (' + str(totalSeats[key]) + u' Plätze)', ls='-', aa=True)

	total = sum([totalSeats[key] for key in bibKeys[bibKey]])
	x1 = np.arange(nVals)
	y1 = np.asarray(totalOccupied)
	axarr[0].plot(x1, y1, label = u'KIT-Bibliothek Süd' + u' (' + str(total) + u' Plätze)', ls='-', aa=True)

	box = axarr[0].get_position()
	axarr[0].set_position([box.x0, box.y0, box.width * 0.74, box.height])
	box = axarr[1].get_position()
	axarr[1].set_position([box.x0, box.y0, box.width * 0.74, box.height])
	axarr[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
	axarr[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))

	axarr[0].set_title(u'Platzverteilung ' + bibNames[bibKey])
	axarr[0].set_ylabel(u'Belegte Plätze')
	axarr[1].set_ylabel(u'Belegte Plätze')
	plt.xlabel(u'Datum/Uhrzeit (UTC+1)')
	plt.show()

if (len(sys.argv) < 3):
	plotOccupance("KITCS1")
else:
	plotOccupance(sys.argv[1])
