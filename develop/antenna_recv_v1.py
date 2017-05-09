#!/usr/bin/env python
###############################################
## This is version 1.                        ##
## Last modified 2015.06.30                  ##
## Any errors, contact astrofanlee@gmail.com ##
###############################################

import socket
import time
import threading
import os
import Queue

def print_to_screen(status_dict):
    '''Show antenna status dict to screen'''
    os.system('clear') # Clear the screen.
    # Print the title.
    print ' No.\tAz.\tAlt.\tAltOn\tAltWarn\tAltLim\tOnline'
    # Print value for each antenna.
    keys = status_dict.keys() # Get keys in dict.
    keys.sort() # Sort keys to output data with antenna number in a small to large sequence.
    for i in keys:
        print ' ' + str(i) + '\t',
        print str(status_dict[i])[2:-2].replace("', '", '\t')
    #print '-----------------------------------------------------'
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

def show(port_range, que, evt):
    '''
    The subthread show.
    Receive data, parse data and print status to screen.
    '''
    antenna_status = {} # Use dict to store antenna data.
    # Initialize the dict.
    for i in range(num_antenna):
        antenna_status[i+1] = '-----','-----','-----','---', '---', '---'
    while not evt.isSet(): # when not terminated, do the loop.
        time0 = time.time() # Take down last refresh time.
        while not evt.isSet(): # when not terminated, do the loop.
            try:
                serial_data = que.get(timeout=0.02) # Get data from main thread; Block for 0.02 second if no data obtained.
                Start_flag, Az, Alt, Status, Online, SN, End_flag = serial_data.strip().split(',') # Split data to elements.
            except:
                continue
            if (Start_flag == '$') and (End_flag == '*'): # Ensure valid data.
                SN = int(SN[4:]) # Antenna number; Use int type to ensure print_to_screen() outputs in a human-readable sequence.
                AltOn, AltWarn, AltLimit = parse_status(Status) # Parse status.

                Online = 'OFF' if Online == 1 else 'ON'
                antenna_status[SN] = Az, Alt, AltOn, AltWarn, AltLimit, Online # Store antenna to dict. 
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
    ip_port = [remoteIP, localIP, localPort] # Convenience for params transfer.
    que = Queue.Queue(50) # Data exchange between threads.
    evt = threading.Event() # Inform subthread to exit.
    show = threading.Thread(target=show, args=(ip_port, que, evt)) # Build subthread.
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
        
