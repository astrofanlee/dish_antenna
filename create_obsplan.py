angle = ['10\t66\t', '180\t11\t']

f = open('obsplan_tmp.txt', 'w')

year = '2015\t'
month = '11\t'
day = 22
sec = '1\t'

dish = '1-14,16'

# write instruction first.
f.write('# This is the file of observation plan. Lines starting with "#" will be ignored.\n# When program is running, you can update the file to change your observation plan.\n# Use "stop" to end an observation plan.\n# Any problems, contact astrofanlee@gmail.com\n#Year   Month   Day     Hour    Min     Sec     Az.     Alt.    Antennas(Use "-" for continuous)\n')

for hour in xrange(18, 18+30, 1):
    if hour == 24: day += 1
    hour = hour % 24
    for min in xrange(0, 60, 5):
        f.write('%s%s%s\t%s\t%s\t%s%s%s\n' % (year, month, str(day), hour, min, sec, angle[min%2], dish))

f.write('stop\n')
f.close()

