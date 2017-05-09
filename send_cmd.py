## python send_cmd.py antenna_number your_cmd_without_\r\n
## Example:
## python send_cmd.py 3 PX120.0PY33.8GO
## python send_cmd.py 6 XV122
## python send_cmd.py 10 ST

import socket
import sys

remoteIP = '192.168.1.100'
localIP = '192.168.1.11'
localPort = 10001

antNo = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((localIP, localPort))
server_address = (remoteIP, 10000+antNo)

cmd = sys.argv[2]

ends = '\x0d\x0a'

sent = sock.sendto(cmd+ends, server_address)
print 'Send', sent, 'bytes.'
sock.close()

