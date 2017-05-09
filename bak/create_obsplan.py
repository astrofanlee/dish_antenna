angle = ['100\t66\t', '270\t11\t']

f = open('obsplan_tmp.txt', 'w')

year = '2015\t'
month = '11\t'
day = 19
sec = '1\t'

dish = '1-16'

for hour in xrange(18, 18+30, 1):
    if hour == 24: day += 1
    hour = hour % 24
    for min in xrange(0, 60, 5):
        f.write('%s%s%s\t%s\t%s\t%s%s%s\n' % (year, month, str(day), hour, min, sec, angle[min%2], dish))

f.write('stop\n')
f.close()

