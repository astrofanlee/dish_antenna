#!/usr/bin/env  python
###############################################
##  This version 2.                          ##
##  Last modified 2015.09.18                 ##
## Any errors, contact astrofanlee@gmail.com ##
###############################################

import socket
import time
import sys

remoteIP = '192.168.1.100'
localIP = '192.168.1.11'
localPort = 10001 # antenna_recv uses 10000; obsplan uses 10002.
ends = '\x0d\x0a' # \r\n
Alt_minimum = 10.00 # degree; Minimum altitude.
Alt_maximum = 88.00 # degree; Maximum altitude; Antenna 3 warns at 84 degree.

def parse_ants(ants_str, antenna_number = 16):
    '''
    Parse input antennas from 'x-y' to (x, x+1, x+2, ..., y).
    '''
    ants_str = ants_str.strip().replace(' ', '')
    if ants_str[-1] == ',': ants_str = ants_str[:-1]
    if '-' in ants_str:
        ants_str = ants_str.strip().split(',')
        ants = []
        for ant_i in ants_str:
            if '-' in ant_i:
                ant_extend = map(int, ant_i.split('-'))
                ants += range(ant_extend[0], ant_extend[1]+1)
            else:
                ants += [int(ant_i)]
        return ants
    else:
        return map(int, ants_str.strip().split(','))

def config(config_ini = 'config.ini', remoteIP = remoteIP, localIP = localIP, localPort = localPort, output = 'Yes'):
    '''
    Send config.ini to antennas.
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Enable complex.
    sock.bind((localIP, localPort)) # Use port 10001 to send; Can be any available port.
    sent_status = 0 # To check if sent successfully.
    fconfig = open(config_ini, 'r') # Open config.ini
    for line in fconfig:
        if line.startswith('DXDY'):  # Find DXDY line.
            antNo, DXDY = line.strip().split('=')
            antNo = int(antNo[4:])
            server_address = (remoteIP, 10000+antNo) # Different ports are connected to different antennas.
            cmd = DXDY + ends # Build command.
            sent = sock.sendto(cmd, server_address) # Send command.
            if sent == 0: # Check if sent successfully.
                print 'Antenna', str(antNo), 'config failed.'
                sent_status += 1 # Take down failed sents.
            time.sleep(0.01)
    sock.close() # Close socket to release port.
    if sent_status == 0:
        if output == 'Yes':
            print 'Antennas successfully configured.'
    else:
        print str(sent_status), 'antenna configuration failed.'
    return

def run(antNo, px, py, remoteIP = remoteIP, localIP = localIP, localPort = localPort, Alt_minimum = 10.00, Alt_maximum = 88.00, output = 'Yes'):
    '''
    Send position command to antennas. 
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((localIP, localPort))
    try:
        px = float(px)
        py = float(py)
        px = max(0., min(360., px))
        py = max(Alt_minimum, min(Alt_maximum, py))
        cmd = 'PX'+str(px)+'PY'+str(py)+'GO' + ends
        cmd_name = 'pointto'
    except ValueError: # Any strings will stop antenna.
        cmd = 'ST' + ends
        cmd_name = 'stop'

    for antNo_i in parse_ants(antNo):
        server_address = (remoteIP, 10000+antNo_i)
        sent = sock.sendto(cmd, server_address)
        if sent != 0:
            if cmd_name == 'pointto':
                if output == 'Yes':
                    print 'Position command for dish ' + str(antNo_i) + ' sent.'
            elif cmd_name == 'stop':
                if output == 'Yes':
                    print 'Stop command for dish ' + str(antNo_i) + ' sent.'
            else:
                print 'Unknown command', cmd_name, 'Please check.'
        else:
            print 'Warning: command for dish ' + str(antNo_i) + ' send failed! Please redo!'
        time.sleep(0.01)
    sock.close()
    return

if __name__ == '__main__':
    try:
        run(sys.argv[1], sys.argv[2], sys.argv[3])
    except:
        try:
            run(sys.argv[1], sys.argv[2], 'st')
        except:
            config(sys.argv[1])

