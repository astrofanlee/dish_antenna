###############################################
##  This is version 1.                       ##
##  Last modified 2015.06.30                 ##
## Any errors, contact astrofanlee@gmail.com ##
###############################################

import datetime as dt
import socket
import time
import sys

def parse_ants(ants_str):
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

def total_sec(td):
    #return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    return td.microseconds/1e6 + td.seconds + td.days * 86400

def get_plan(obsplan_file, plan_length = 60, stop_cmd = 'stop'):
    '''
    Return a list containing observation plans within plan_length seconds in the future.
    Example list:
        [[datetime.datetime(2015, 1, 1, 12, 0, 15), 194.34, 44.78, (2,3,8,15,16)],
         [datetime.datetime(2015, 1, 1, 12, 5, 30), 124.62, 22.49, (2,3,8,15,16)],
         [datetime.datetime(2015, 1, 1, 14, 31, 10), 202.11, 59.76, (1,5,10,12,15)],
         ... ...
         [datetime.datetime(2015, 1, 1, 14, 31, 10), 202.11, 59.76, (1,5,10)],
         ['stop']
        ]
    '''
    obsplan_list = []
    with open(obsplan_file, 'r') as fin:
        time_now = dt.datetime.now()
        for line in fin:
            if line.startswith('#'):
                continue
            elif (line[:4].lower() == stop_cmd) or (line == ''):
                obsplan_list += [['stop']]
                return obsplan_list
            else:
                try:
                    linedata = line.strip().split()
                    plan_dt = dt.datetime(*map(int, linedata[:6]))
                    #if (plan_dt - time_now).total_seconds() > plan_length:
                    if total_sec(plan_dt - time_now) > plan_length:
                        return obsplan_list
                    #elif (plan_dt - time_now).total_seconds() >= 0:
                    elif total_sec(plan_dt - time_now) >= 0:
                        obsplan_list += [[dt.datetime(*map(int, linedata[:6])), float(linedata[6]), max(Alt_min, min(Alt_max, float(linedata[7]))), parse_ants(linedata[8]), line.strip()]]
                        continue
                    else:
                        continue
                except:
                    continue

if __name__ == '__main__':
    remoteIP = '192.168.1.100' # Serial server IP.
    localIP = '192.168.1.11'     # Local IP.
    localPort = 10002          # Local Port; antenna_send uses 10000, antenna_recv uses 10001.
    
    obsplan_file = 'obsplan.txt'
    obsplan_status_file = 'obsplan.status' # Output file.
    Alt_min = 15.0 # degree; Minimum altitude for security.
    Alt_max = 88.5 # degree; Maximum altitude for security.
    check_time = 60 # seconds; Maximum time interval to check the obsplan.txt file; Do not set too long.
    stop_cmd = 'stop' # If encountering this line in obsplan_file, program will stop and exit.
    ###################permit_past = -1 # Observation plan which is permit_past second in the past is permitted. This is due to time consumes in processing multiple plans with exatly the same date and time. 
    
    ends = '\x0d\x0a' # \r\n
    
    executed_item = ''
    try:
        while 1:
            plan_list = get_plan(obsplan_file, check_time, stop_cmd)
            if plan_list == []:
                time.sleep(check_time-1) # When no plan, wait check_time; A possible bug!!!
            else:
                if plan_list[0] == executed_item:
                    continue
                with open(obsplan_status_file, 'a') as fou:
                    for plan_item in plan_list:
                        if plan_item == [stop_cmd]:
                            fou.write(dt.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + 'Exited.\n')
                            fou.close()
                            exit(0)
                        else:
                            plan_dttm, plan_az, plan_alt, plan_ants, plan_input = plan_item
                            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket
                            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permit multiplex.
                            sock.bind((localIP, localPort))
                            cmd = 'PX'+str(plan_az) + 'PY'+str(plan_alt) + 'GO'+ends # unsure.
                            #time.sleep(max(0, (plan_dttm - dt.datetime.now()).total_seconds()))
                            time.sleep(max(0, (plan_dttm - dt.datetime.now()).seconds))
                            for i_ant in plan_ants:
                                server_address = (remoteIP, 10000+i_ant)
                                sock.sendto(cmd, server_address)
                                time.sleep(0.01)
                            print dt.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + plan_input + '\t# Executed.\n'
                            fou.write(dt.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + plan_input + '\t# Executed.\n')
                            sock.close()
                executed_item = plan_item
    except KeyboardInterrupt:
        exit()
    except SystemExit:
        exit()
    except:
        with open(obsplan_status_file, 'a') as fou:
            fou.write(dt.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + 'Error encoutered.\n')
        raise

