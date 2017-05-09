###################################
# Last modified: 20150701         #
# Reply to: astrofanlee@gmail.com #
###################################

How to use?

Part 1:
1. Configure serial server: change the work mode of each port to TCP/UDP socket and data format to raw and protocol to UDP.
2. Add local IP and local port (default=10000)
3. Save configurations.
4. Restart serial server.

Part 2:
1. Run antenna_recv.py
sudo python antenna_recv.py
You'll see the antenna status.
Use Ctrl+C to exit.

2. Run antenna_send.py
(1) Interactive mode:
sudo python antenna_send.py
Then input antenna number, Azimuth and Altitude according to prompt.
Use Ctrl+C to exit.
(2) Run once mode:
sudo python antenna_send.py antNo Az Alt
(3) Configure angles:
sudo python antenna_send.py config.ini

3. Address already in use?
If program exits abnormly, you'll encounter following error:
socket.error: [Errno 98] Address already in use

To solve the problem, run:
sudo netstat -apn | grep 10000
where 10000 is the local port. And you'll get something like:
udp        0      0 192.168.1.8:10000           0.0.0.0:*       5622/python
where 5622 is the PID. 
Run following command to kill it:
sudo kill -9 5622
Okay now!

4. Cannot receive data?
When OS is newly installed, sock.recvfrom() in antenna_recv.py cannot work. Run:
iptable -F
will solve the problem.


