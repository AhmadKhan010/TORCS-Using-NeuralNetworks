import sys
import argparse
import socket
import driver  # Ensure this module exists and works with Python 3

# Configure the argument parser
parser = argparse.ArgumentParser(description='Python client to connect to the TORCS SCRC server.')
parser.add_argument('--host', action='store', dest='host_ip', default='localhost',
                    help='Host IP address (default: localhost)')
parser.add_argument('--port', action='store', type=int, dest='host_port', default=3001,
                    help='Host port number (default: 3001)')
parser.add_argument('--id', action='store', dest='id', default='SCR',
                    help='Bot ID (default: SCR)')
parser.add_argument('--maxEpisodes', action='store', dest='max_episodes', type=int, default=1,
                    help='Maximum number of learning episodes (default: 1)')
parser.add_argument('--maxSteps', action='store', dest='max_steps', type=int, default=0,
                    help='Maximum number of steps (default: 0)')
parser.add_argument('--track', action='store', dest='track', default=None,
                    help='Name of the track')
parser.add_argument('--stage', action='store', dest='stage', type=int, default=3,
                    help='Stage (0 - Warm-Up, 1 - Qualifying, 2 - Race, 3 - Unknown)')

arguments = parser.parse_args()

# Print summary
print('Connecting to server host ip:', arguments.host_ip, '@ port:', arguments.host_port)
print('Bot ID:', arguments.id)
print('Maximum episodes:', arguments.max_episodes)
print('Maximum steps:', arguments.max_steps)
print('Track:', arguments.track)
print('Stage:', arguments.stage)
print('*********************************************')

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as msg:
    print('Could not make a socket:', msg)
    sys.exit(-1)

# One-second timeout
sock.settimeout(1.0)

shutdownClient = False
curEpisode = 0
verbose = False

d = driver.Driver(arguments.stage)  # Ensure driver.Driver is compatible

while not shutdownClient:
    while True:
        print('Sending id to server: ', arguments.id)
        buf = arguments.id + d.init()
        try:
            sock.sendto(buf.encode('utf-8'), (arguments.host_ip, arguments.host_port))
        except socket.error as msg:
            sys.exit(-1)
        try:
            buf, addr = sock.recvfrom(1000)
            buf = buf.decode('utf-8')
        except socket.error as msg:
            continue
        if buf.find('***identified***') >= 0:
            break

    # --- Step-based main loop ---
    if arguments.max_steps == 0:
        arguments.max_steps = 1000000
    for step in range(arguments.max_steps, 0, -1):
        try:
            buf, addr = sock.recvfrom(1000)
            buf = buf.decode('utf-8')
        except socket.error as msg:
            print("Didn't get response from server:", msg)
            continue

        if verbose and buf is not None:
            print('Received: ', buf)

        if buf and '***shutdown***' in buf:
            d.onShutDown()
            shutdownClient = True
            print('Client Shutdown')
            break

        if buf and '***restart***' in buf:
            d.onRestart()
            print('Client Restart')
            break

        # Only drive and send every 3rd step
        if step % 3 == 0 and buf:
            outmsg = d.drive(buf)
            if verbose and outmsg:
                print('Sending: ', outmsg)
            if outmsg:
                try:
                    sock.sendto(outmsg.encode('utf-8'), (arguments.host_ip, arguments.host_port))
                except socket.error as msg:
                    print("Failed to send data:", msg)
                    sys.exit(-1)
        # End episode if steps run out
        if step == 1:
            try:
                sock.sendto('(meta 1)'.encode('utf-8'), (arguments.host_ip, arguments.host_port))
            except socket.error as msg:
                print("Failed to send data:", msg)
                sys.exit(-1)

    curEpisode += 1
    if curEpisode == arguments.max_episodes:
        shutdownClient = True

sock.close()