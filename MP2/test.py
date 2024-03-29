#这个文件 是每一个node的运行文件，用来创建一个node
import sys
import heapq

import node
from node import Node
from basic_node import Basic_Node

def test_send():
    basic_node = Basic_Node(8081)
    basic_node.Connect_to_Servers(8080)
    while True:
        message = sys.stdin.readline()[:-1]
        if not message:
            break
        basic_node.Send_msg(message)
    return
def init_node():
    basic_node = Basic_Node(8080)
    return basic_node
def test_heap():
    temp = [[2,3,"4"],[4,2,"5"],[1,10,"3"]]
    heapq.heapify(temp)
    print(temp)

def test_Connect():
    node1 = Node("Lucky",2,"node1_config.txt", 8081)

    return

def main():
    #test
    #test_send()
    #test_Connect()
    test_heap()
    return

    


if __name__ == '__main__':
    main()
