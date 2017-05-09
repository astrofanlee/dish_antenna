#!/usr/bin/env python
###############################################
## This is version 2.                        ##
## Last modified 2015.09.20                  ##
## Any errors, contact astrofanlee@gmail.com ##
###############################################

import socket
import time
import threading
import os
import Queue
import numpy
import antenna_send

def print_to_screen(status_dict):
    '''Show antenna status dict to screen'''
    os.system('clear') # Clear the screen.
    # Print the title.
    print ' No.\tAz.\tAlt.\tAltOn\tAltWarn\tAltLim\tOnline\tLoops'
    # Print value for each antenna.
    #antenna_status[i+1] = {'Az':'-----', 'Alt':'-----', 'AltOn':'-----', 'AltWarn':'---', 'AltLimit':'---', 'Online':'OFF', 'Loops': str(loops[i][1]), 'Update'time.time()
    for key,value in status_dict.iteritems():
        print ' %s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (key, value['Az'], value['Alt'], value['AltOn'], value['AltWarn'], value['AltLimit'], value['Online'], value['Loops'])
    print '===================================================='
    print time.strftime(' Time: %Y-%m-%d %H:%M:%S')
    return

def parse_status(Status):
    '''
    Parse antenna status byte with following format:
        bit7: Altitude service enabled.
        bit6: Altitude warning.
        bit5: Altitude AntiClockwise limited.
        bit4: Altitude Clockwise limited.
        bit3: Azimuth service enabled.
        bit2: Azimuth warning.
        bit1: Azimuth AntiClockwise limited.
        bit0: Azimuth Clockwise limited.
    Note:
        Now, Azimuth limit is not used, so Azimuth status is not returned.
    '''
    Status = int(Status) # Change to int type in order to right shift.
    Status >>= 4         # Remove Azimuth bits.
    if Status % 2 == 1:  # This is bit4.
        AltLimit = 'Down'
        Status >>= 1
        if Status % 2 == 1:    # This is bit5.
            AltLimit = 'Error' # bit4 must different from bit5.
    else:
        AltLimit = '  '
        Status >>= 1
        if Status % 2 == 1: # This is bit5.
            AltLimit = 'Up'
    Status >>= 1
    AltOn = 'Enable' if Status % 2 == 0 else 'Unable' # This is bit6.
    Status >>= 1
    AltWarn = 'WARN' if Status % 2 == 1 else '  '     # This is bit7.
    return AltOn, AltWarn, AltLimit
#def judge_loop(Az_new, Az_old):
#    if   Az_new - Az_old < -355: return 1
#    elif Az_new - Az_old >  355: return -1
#    else: return 0

def process_dict(status_dict, new_data):
    #antenna_status[i+1] = 'Az', 'Alt', 'AltOn', 'AltWarn', 'AltLim', 'OFF', loops, time.time()
    SN, Az, Alt, AltOn, AltWarn, AltLimit = new_data
    time_now = time.time()
    #unconfig = 0 # number of unconfiged dishes.
    for key,value in status_dict.iteritems():
        if time_now - value['Update'] > 2:
            status_dict[key]['Online'] = 'OFF'
    if time_now - status_dict[SN]['Update'] < 2:
        status_dict[SN]['Update'] = time_now
    elif status_dict[SN]['Online'] = 'OFF':
        antenna_send.config()#output='No')
    else:
        print 'Unknown Online value.'
        exit()
    status_dict[SN]['Loops'] += int((status_dict[SN]['Loops'] - float(Az)) / 350)
    status_dict[SN]['Az'] = Az
    status_dict[SN]['Alt'] = Alt
    status_dict[SN]['AltOn'] = AltOn
    status_dict[SN]['AltWarn'] = AltWarn
    status_dict[SN]['AltLimit'] = AltLimit
    return

def show(que, evt):
    '''
    The subthread show.
    Receive data, parse data and print status to screen.
    '''
    loops = numpy.loadtxt('dish_loops.txt', dtype='int')
    antenna_status = {} # Use dict to store antenna data.
    # Initialize the dict.
    for i in xrange(num_antenna):
        antenna_status[i+1] = {'Az':'-----', 'Alt':'-----', 'AltOn':'-----', 'AltWarn':'---', 'AltLimit':'---', 'Online':'OFF', 'Loops': loops[i][1], 'Update':time.time()}
    
    while not evt.isSet(): # when not terminated, do the loop.
        time0 = time.time() # Take down last refresh time.
        while not evt.isSet(): # when not terminated, do the loop.
            try:
                serial_data = que.get(timeout=0.02) # Get data from main thread; Block for 0.02 second if no data obtained.
                Start_flag, Az, Alt, Status, Online, SN, End_flag = serial_data.strip().split(',') # Split data to elements.
            except:
                continue
            if (Start_flag == '$') and (End_flag == '*'): # Ensure valid data.
                SN = int(SN[4:])
                AltOn, AltWarn, AltLimit = parse_status(Status) # Parse status.

                #Online = 'OFF' if Online == 1 else 'ON'
                new_data = SN, Az, Alt, AltOn, AltWarn, AltLimit # new_data of one dish.
                antenna_status = process_dict(antenna_status, new_data)
                #antenna_status[SN] = Az, Alt, AltOn, AltWarn, AltLimit, 'OnOff', '1' # Store antenna to dict. 
            #print 'size = ', que.qsize(), 'left = ', 50-que.qsize() # Check if the Queue is not enough.
            if time.time() - time0 >= refresh_time: # refresh_time.
                print_to_screen(antenna_status)
                break
    #print '==== show exits ===='

if __name__ == '__main__':    
    remoteIP = '192.168.1.100'
    localIP = '192.168.1.11'
    localPort = 10000 # antenna_send uses 10001; obsplan uses 10002.

    refresh_time = 0.5 # seconds; Time interval of screen output.
    num_antenna = 16 # Number of antennas.

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket.
    sock.bind((localIP, localPort))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Enable multiplex
    #ip_port = [remoteIP, localIP, localPort] # Convenience for params transfer.
    que = Queue.Queue(50) # Data exchange between threads.
    evt = threading.Event() # Inform subthread to exit.
    show = threading.Thread(target=show, args=(que, evt)) # Build subthread.
    show.start() # Start subthread.

    # Remind user whether Antenna Power has been turned on.
    print 'Have you turned on the power for dish antennas?'

    # The main thread will receive UDP packets sent to localPort of localIP from remoteIP, and then transfer packet to subthread show.
    try:
        while 1:
            data, address = sock.recvfrom(1000) # Receive UDP packets.
            if address[0] != remoteIP: # Only accept packets from remoteIP
                continue
            else:
                que.put(data) # Transfer data to subthread.
    except KeyboardInterrupt:
        #print 'before event set'
        evt.set() # Inform subthread to exit.
        #print 'after event set'
        show.join() # Wait subthread to end.
        #print 'before sock close'
        sock.close() # Close socket to release localPort.
        #print 'after sock close'
        
