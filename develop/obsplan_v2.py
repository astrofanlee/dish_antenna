###############################################
##  This is version 2.                       ##
##  Last modified 2015.09.18                 ##
## Any errors, contact astrofanlee@gmail.com ##
###############################################

import datetime as dt
import time
import sys

import antenna_send

def total_sec(td):
    return td.microseconds/1e6 + td.seconds + td.days * 86400

def get_plan(obsplan_file, plan_length = 60, exit_cmd = 'exit'):
    '''
    Return a list containing observation plans within plan_length seconds in the future.
    Example list:
        [[datetime.datetime(2015, 1, 1, 12, 0, 15), 'config', 'config', (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)],
         [datetime.datetime(2015, 1, 1, 12, 5, 30), 124.62, 22.49, (2,3,8,15,16)],
         [datetime.datetime(2015, 1, 1, 12, 44, 00), st, st, (2,3,8,15,16)],
         [datetime.datetime(2015, 1, 1, 14, 31, 10), 202.11, 59.76, (1,5,10,12,15)],
         ... ...
         [datetime.datetime(2015, 1, 1, 14, 31, 10), 202.11, 59.76, (1,5,10)],
         ['exit']
        ]
    '''
    obsplan_list = []
    with open(obsplan_file, 'r') as fin:
        time_now = dt.datetime.now()
        for line in fin:
            if line.startswith('#'):
                continue
            elif (line[:4].lower() == exit_cmd) or (line == ''):
                obsplan_list += [['exit']]
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
                        try:
                            px = max(0., min(360., float(linedata[6])))
                            py = max(antenna_send.Alt_minimum, min(antenna_send.Alt_maximum, float(linedata[7])))
                        except ValueError:
                            if linedata[6] == 'config':
                                obsplan_list += [[dt.datetime(*map(int, linedata[:6])), 'config', 'config', '1-16', line.strip()]]
                                continue
                            else:
                                obsplan_list += [[dt.datetime(*map(int, linedata[:6])), 'st', 'st', linedata[8], line.strip()]]
                        obsplan_list += [[dt.datetime(*map(int, linedata[:6])), px, py, linedata[8], line.strip()]]
                        continue
                    else:
                        continue
                except:
                    continue

if __name__ == '__main__':
    obsplan_file = 'obsplan.txt'
    obsplan_status_file = 'obsplan.status' # Output file.
    check_time = 60 # seconds; Maximum time interval to check the obsplan.txt file; Do not set too long.
    exit_cmd = 'exit' # If encountering this line in obsplan_file, program will stop and exit.
    ###################permit_past = -1 # Observation plan which is permit_past second in the past is permitted. This is due to time consumes in processing multiple plans with exatly the same date and time. 
    
    executed_item = ''
    try:
        while 1:
            plan_list = get_plan(obsplan_file, check_time, exit_cmd)
            if plan_list == []:
                time.sleep(check_time-1) # When no plan, wait check_time; A possible bug!!!
            else:
                if plan_list[0] == executed_item:
                    continue
                with open(obsplan_status_file, 'a') as fou:
                    for plan_item in plan_list:
                        if plan_item == [exit_cmd]:
                            antenna_send.run('1-16', 'st', 'st', output = 'No')
                            fou.write(dt.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + 'Exited.\n')
                            fou.close()
                            exit(0)
                        else:
                            plan_dttm, plan_az, plan_alt, plan_ants, plan_input = plan_item
                            time.sleep(max(0, (plan_dttm - dt.datetime.now()).seconds))
                            if plan_az == 'config':
                                antenna_send.config(output = 'No')
                            else:
                                antenna_send.run(plan_ants, plan_az, plan_alt, output = 'No')
                            print dt.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + plan_input + '\t# Executed.\n'
                            fou.write(dt.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + plan_input + '\t# Executed.\n')
                executed_item = plan_item
    except KeyboardInterrupt:
        exit()
    except SystemExit:
        exit()
    except:
        with open(obsplan_status_file, 'a') as fou:
            fou.write(dt.datetime.now().strftime('[%Y-%m-%d %H:%M:%S] ') + 'Error encoutered.\n')
        raise

