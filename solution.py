from socket import *
import os
import sys
import struct
import time
import select
import binascii
import ipaddress

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 1


# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():
    # In the sendOnePing() method of the ICMP Ping exercise ,firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    # Make the header in a similar way to the ping exercise.
    # Append checksum to the header.

    myChecksum = 0
    ID = os.getpid() & 0xFFFF  # Return the current process i

    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)

    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    alltraces = []  # This is your list to contain all traces

    for ttl in range(1, MAX_HOPS):
        print(alltraces)
        thistrace = []
        thistrace.append(ttl)
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)
            # Make a raw socket named mySocket
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []:
                    print('1')# Timeout
                    thistrace.append("*")
                    thistrace.append("Request timed out.")
                    # You should add the list above to your all traces list
                    alltraces.append(thistrace)
                    continue
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                rtt = str(round((timeReceived - startedSelect) * 1000, 0))
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print("2")
                    thistrace.append("*")
                    thistrace.append("Request timed out.")
                    # You should add the list above to your all traces list
                    alltraces.append(thistrace)
                    continue
            except timeout:
                print("timeout")
                continue

            else:
                print('3')
                # Fetch the icmp type from the IP packet
                typeData = recvPacket[20:21]
                types = struct.unpack("b", typeData)
                hostData = recvPacket[12:16]
                hostIP = str(ipaddress.IPv4Address(hostData))
                try:  # try to fetch the hostname
                    hostName, aliaslist, ipaddrlist = gethostbyaddr(hostIP)
                except herror:  # if the host does not provide a hostname
                    hostName = "hostname not returnable"
                if types == 11:
                    print("type 11")
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 +
                                                                bytes])[0]
                    thistrace.append(rtt)
                    thistrace.append(hostIP)
                    this.trace.append(hostName)
                    alltraces.append(thistrace)
                    continue
                elif types == 3:
                    print("Type 3")
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    thistrace.append("*")
                    thistrace.append("Request timed out.")
                    alltraces.append(thistrace)
                    return alltraces
                elif types == 0:
                    print("type 0")
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    thistrace.append(rtt)
                    thistrace.append(hostIP)
                    this.trace.append(hostName)
                    alltraces.append(thistrace)
                    print(alltraces)
                    return alltraces
                else:
                    print('here')

                    # Fill in start
                    # If there is an exception/error to your if statements, you should append that to your list here
                    # Fill in end
                break
            finally:
                mySocket.close()


if __name__ == '__main__':
    get_route("google.com")
