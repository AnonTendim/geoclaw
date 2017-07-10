
import csv
import locale




import numpy
import matplotlib.pyplot as plt
import datetime, time
import pandas as pd
 
columns = ['Time', 'Difference']
data = pd.read_csv('/Users/anonymous/clawpack_src/clawpack-v5.4.1rc-beta/geoclaw/examples/storm-surge/matthew/gaugeReportHour.csv', header=None, names=columns)

converted = []
tide = []
landfall_dt = datetime.datetime(2016, 10, 7, 6) - \
           datetime.datetime(2016, 1, 1, 0)

for x in data.Time:
	if (x != 'Time'):
		datetime_object = datetime.datetime.strptime(x, '%x  %H:%M')
		t = datetime_object - landfall_dt
		second = (time.mktime(t.timetuple())) - time.mktime(datetime.datetime(2016, 1, 1, 1, 0).timetuple())
		day = second / (60.0**2 * 24.0)
		converted.append(day)

for y in data.Difference:
	if (y != 'Difference'):
		print y
		# y = y.astype(float)
		tide.append(y)
plt.plot(converted, tide)
plt.show()