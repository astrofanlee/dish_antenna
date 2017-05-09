#!/usr/bin;env  python

import socket
import time
import sys

def send_config(config_ini):
    '''
    Send config.ini to antennas.
    '''
    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket.
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Enable complex.
    #sock.bind((localIP, 10001)) # Use port 10001 to send; Can be any available port.
    sent_status = 0 # To check if sent successfully.
    fconfig = open(sys.argv[1], 'r') # Open config.ini
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
        print 'Antennas successfully configured.'
    else:
        print str(sent_status), 'antenna configuration failed.'
    return

if __name__ == '__main__':
    remoteIP = '192.168.1.100'
    localIP = '192.168.1.11'
    localPort = 10001 # antenna_recv uses 10000; obsplan uses 10002.
    Alt_minimum = 15.00 # degree; Minimum altitude.
    Alt_maximum = 88.50 # degree; Maximum altitude; Antenna 3 warns at 84 degree.

    ends = '\x0d\x0a' # \r\n    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((localIP, localPort))
    if len(sys.argv) == 1: # The interactive mode.
        print '\n======== Interactive Mode ========'
        try:
            while 1:
                params = raw_input('Input Antenna No. Az. Alt.: ') # Get inputs.
                if params == '': continue
                params = params.strip().split()
                try:
                    antNo = int(params[0])
                except:
                    print 'Invalid antenna number. '
                    continue
                if antNo < 1 or antNo > 16: # Ensure 0<antNo<17
                    print 'Invalid antenna number. '
                    continue
                #sock.bind((localIP, 10001))
                server_address = (remoteIP, 10000+antNo)
                try:
                    px = float(params[1])
                    py = float(params[2])
                    px = max(0., min(360., px)) # Ensure valid degree.
                    py = max(Alt_minimum, min(Alt_maximum, py))  # Ensure valid degree.
                    cmd = 'PX'+str(px)+'PY'+str(py)+'GO' + ends
                    cmd_name = 'pointto'
                except ValueError:
                    cmd = 'ST' + ends
                    cmd_name = 'stop'
                sent = sock.sendto(cmd, server_address)
                if sent != 0:
                    if cmd_name == 'pointto':
                        print 'Position command sent.'
                    elif cmd_name == 'stop':
                        print 'Stop command sent.'
                    else:
                        print 'Unknown command', cmd_name, 'Please check.'
                else:
                    print 'Warning: command send failed! Please redo!'
        except:
            sock.close()
            print '\n'
            exit()
    else: # Run once mode.
        try:
            antNo = int(sys.argv[1])
        except ValueError:
            if sys.argv[1].endswith('.ini'): # If use config.ini
                send_config(sys.argv[1])
                exit()
            else:
                print 'Unknow command.'
                exit()
        #sock.bind((localIP, 10001))
        server_address = (remoteIP, 10000+antNo)
        try:
            px = float(sys.argv[2])
            py = float(sys.argv[3])
            px = max(0., min(360., px))
            py = max(10., min(Alt_maximum, py))
            py = max(Alt_minimum, min(Alt_maximum, py))
            cmd = 'PX'+str(px)+'PY'+str(py)+'GO' + ends
            cmd_name = 'pointto'
        except ValueError: # Any strings will stop antenna.
            cmd = 'ST' + ends
            cmd_name = 'stop'
        sent = sock.sendto(cmd, server_address)
        sock.close()
        if sent != 0:
            if cmd_name == 'pointto':
                print 'Position command sent.'
            elif cmd_name == 'stop':
                print 'Stop command sent.'
            else:
                print 'Unknown command', cmd_name, 'Please check.'
        else:
            print 'Warning: command send failed! Please redo!'


