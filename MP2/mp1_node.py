#这个文件 是每一个node的运行文件，用来创建一个node
import sys
import threading

import node
from node import Node
from basic_node import Basic_Node


def main():
    #mp1_node {node id} {port} {config file}
    if(len(sys.argv) != 4):
        print("mp1_node {node id} {port} {config file}")
        return
    node_id = sys.argv[1]
    port = int(sys.argv[2])
    config_file = sys.argv[3]
    Node_current = Node(node_id,config_file, port)
    print(Node_current.node_dict)
    print("!!!!!!!!!!!!!!!!!!!!!")
    #一个线程用来收到transaction并且群发
    #thd = threading.Thread(target=Node_current.Send_transactions)
    #thd.start()
    #Node_current.Send_transactions()
    #读取transaction信息，multicast给每个Client
    
    
    print("主线程！！")
    return

    


if __name__ == '__main__':
    main()
