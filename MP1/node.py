import sys
import time

import basic_node
def main():

    # check the required argparse
    if len(sys.argv) < 2:
        print("Invalid command format. Please use the format: node.py node_name ip_address port")

    node_name = sys.argv[1]

    if len(sys.argv) > 2:
        ipaddress = str(sys.argv[2])
    else:
        ipaddress = "127.0.0.1"  # default ip

    if len(sys.argv) > 3:
        port = int(sys.argv[3])
    else:
        port = 1234  # default port

    tcp_node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    tcp_node.connect((ipaddress, port))

    # send node_name to tell the logger that connection has started
    tcp_node.send(("%s %s " % (time.time(), node_name)).encode(encoding='utf-8'))
    time.sleep(0.000001)        # avoid sticky packet problem

    # recv_data = tcp_node.recv(1024)
    # if recv_data.decode() != node_name:
    #     print("error!")
    #6
    while True:
        message = sys.stdin.readline()[:-1]
        if not message:
            break
        tcp_node.send(message.encode(encoding='utf-8'))

    tcp_node.send(("%s %s " % (time.time(), node_name)).encode(encoding='utf-8'))

    tcp_node.close()


if __name__ == '__main__':
    main()
