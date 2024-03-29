import sys
import json
import basic_node
from basic_node import *
class Node(Basic_Node):
    def __init__(self, nodename, file_name, Port):
        super(Node, self).__init__(Port)
        self.name = nodename
        self.accounts = {}
        self.other_node_num = None
        self.max_proposal_priority = 0
        self.priority_num = 0
        self.index = 0
        self.transaction_list = []
        self.transaction_Priority = {}
        self.transaction_index_map = {}
        self.node_dict = {}
        self.Receive_dict = {}
        self.read_config(file_name)
        self.Connect_to_config_nodes()
        #thd = threading.Thread(target=Node.Init_Server, args=(self,Port))#main_thread在持续accept接受(如果没有 就卡住)，new_thread进行信息分析
        #thd.start()
        self.Init_Server(Port)
        self.Send_transactions()
    
    def read_config(self,file_name):
            f=open(file_name,"r")
            line = f.readline().strip() #读取第一行
            self.other_node_num = int(line)
            while line:  # 直到读取完文件
                line = f.readline().strip()  # 读取一行文件，包括换行符
                if(line):
                     self.handle_sentence(line)
            f.close()  # 关闭文件

    def handle_sentence(self,line):
        node_info = line.split()
        if(node_info[1] == "localhost"):
             node_info[1] = "127.0.0.1"
        self.node_dict[node_info[0]] = node_info[1:]#node2 : IP 1234
    
    def Connect_to_config_nodes(self):
        for name in self.node_dict.keys():
            thd = threading.Thread(target=Node.Connect_to_Servers, args=(self,name ,self.node_dict[name][1],self.node_dict[name][0]))
            thd.start()
            #thd不用join 主线程结束 子线程竟然不会死掉( •̀ ω •́ )y
        return

    def Send_transactions(self):
        if(self.Connect_num <= self.other_node_num or len(self.Send_dict.keys()) <=self.other_node_num):
            time.sleep(1)
        while True:
            message = sys.stdin.readline()[:-1]
            if not message:
                break
            #需要在本地做标记
            msg_list = [self.name,message,self.index,0]#发送的Transaction格式[Node1, transaction, index,0]
            self.transaction_index_map[self.index] = message
            current_index = self.index
            self.index = self.index+1
            self.Send_msg(msg_list)
            time.sleep(0.000001) 
            self.handle_Transaction(msg_list,-1)#加入自己的transaction_list -1拿来凑数的
            self_Priority = [self.priority_num,msg_list[1],current_index,1]#self_Priority: [priority_num,transaction,index,1]
            self.handle_Priority(self_Priority)#自己给自己发送Priority
        print("Stop Sending!")
        return
        
    def Init_Server(self,Port):
        self.Server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.Server_socket.bind(("", Port))
        #print("我开始听了！")
        self.Server_socket.listen(30)   
        #多线程进行收消息，每个线程都一直不出来，直到连接结束
        socket_list = []
        while True:
            Clients_socket, _ = self.Server_socket.accept() #return 别的node的套接字对象和address 会一直阻塞在这里！
            socket_list.append(Clients_socket)
            self.Connect_num = self.Connect_num+1
            if(self.Connect_num == self.other_node_num):
                #print("????????????????????????????????????????????????????????")
                break
            #print("有人来啦！")
        for socket_fd in socket_list :
            thd = threading.Thread(target=Node.handle_message, args=(self,socket_fd))#main_thread在持续accept接受(如果没有 就卡住)，new_thread进行信息分析
            thd.start()
            #thd.join()#不需要join

    #处理收到的msg
    def handle_message(self,Clients_socket):
        #处理收到的transaction
        while True:
            recv_data  = Clients_socket.recv(4096)
            if(recv_data):
                message = recv_data.decode()#.split()
                msg_list = json.loads(message)
                #print("Receive message: ", msg_list)
                self.divide_message(msg_list,Clients_socket)#Clients_socket单纯为了建立下clients_socket和client的联系，为了failure detection
                #msg_list = json.loads(message)
                #print("A new Transaction!")
                #print(message)
            else:
                #Clients_socket死掉了
                #!!handle failure
                #print("remove ", self.Receive_dict[Clients_socket], "from the node list")
                failed_node_name = self.Receive_dict[Clients_socket]
                self.Send_socket_list.remove(self.Send_dict[failed_node_name])
                self.Connect_num = self.Connect_num -1
                #Remove msg sent from the failed node
                self.remove_fail_transactions(failed_node_name)
                break
        
    def remove_fail_transactions(self, failed_node_name):
        for i in range(len(self.transaction_list)):
            if(self.transaction_list[i][1] == failed_node_name ):
                #print("找到啦！")
                #list中的结构：[priority_num,node_name,deliverable,transaction, index])
                del self.transaction_list[i]
            continue
#判断是优先队列还是Priority
    def divide_message(self,message,Clients_socket):
        #print("收到信息：!", message)
        if(message[-1] == 0):#Transaction最后一个元素0
            #print("transaction!!")
            self.handle_Transaction(message,Clients_socket)
            self.Send_priority(message)
        elif(message[-1] == 1):#Priority最后一个元素是1
            #print("Priority")
            self.handle_Priority(message)
        else:
            #print("Final Priority")
            self.handle_final_Priority(message)

#处理收到的Transaction
    def handle_Transaction(self,message, Clients_socket):
        #处理收到的transaction
        #收到的Transaction格式[Node1, transaction, index, 0]
        deliverable = 0
        node_name = message[0]
        transaction = message[1]
        index = message[2]
        self.priority_num = self.priority_num+1
        if(self.Connect_num == 0):
            #别的都死掉惹 直接自己处理transaction捏'
            while(len(self.transaction_list)):
                self.Deliver_Transaction(self.transaction_list[0][3])
                heapq.heappop(self.transaction_list)
            self.Deliver_Transaction(transaction)
            return
        #为了failure detection建立Client_socket和transaction的关系
        if(not isinstance (Clients_socket,int) ):
            if(Clients_socket not in self.Receive_dict.keys()):
                self.Receive_dict[Clients_socket] = node_name
        self.transaction_list.append([self.priority_num,node_name,deliverable,transaction, index])
        #print(self.transaction_list)
        #msg_list = json.loads(message)
        return
    
    def Send_priority(self, message):
        #收到的Transaction格式[Node1, transaction, index, 0]
        node_name = message[0]
        transaction = message[1]
        index = message[2]
        priority_num = self.priority_num
        send_socket = self.Send_dict[node_name]
        self.Send_1to1_msg(send_socket, [priority_num,transaction,index,1])
        pass

#处理收到的很多Priority
    def handle_Priority(self,message):
        #message: [priority_num,transaction,index,1]
        priority_num = message[0]
        transaction = message[1]
        index = message[2]
        if(index in self.transaction_Priority.keys()):
            self.transaction_Priority[index][0] = max(self.transaction_Priority[index][0], priority_num)
            self.transaction_Priority[index][1] = self.transaction_Priority[index][1]+1
            if(self.transaction_Priority[index][1] == (self.Connect_num+1)):#当所有的Priority都收到了就将最终Priority发送(包含自己 所以要加一)
                message_list = [transaction, self.transaction_Priority[index][0], index, 2]
                #final_Priority: [Transaction, Priority, index, 2]
                self.Send_msg(message_list)
                #还得让自己知道
                self.handle_final_Priority(message_list)
            elif(self.transaction_Priority[index][1] >= (self.Connect_num+1)):
                print("Shit!!!!")
        else:
            self.transaction_Priority[index] = [priority_num, 1]
        return

#出来收到的Final_Priority:
    def handle_final_Priority(self,message_list):
        #print(message_list)
        #message: [transaction, Priority, index, 2]
        if(self.Connect_num == 0):
            print("哭哭")
        Transaction = message_list[0]
        Final_Priority = message_list[1]
        index = message_list[2]
        self.priority_num = Final_Priority#Priority不会比本地的小，最多和本地的相等
        for i in range(len(self.transaction_list)):
            if(self.transaction_list[i][3] == Transaction and self.transaction_list[i][4] == index):
                #print("找到啦！")
                #list中的结构：[priority_num,node_name,deliverable,transaction, index])
                self.transaction_list[i][0] = Final_Priority#修改Priority的值
                self.transaction_list[i][2] = 1#修改Deliverable
                break
            continue
        heapq.heapify(self.transaction_list)
        #print("The Heapq is!!:", self.transaction_list)
        if(self.transaction_list[0][2]):#First One Deliverable！！
            #print("deliver :", self.transaction_list[0][3])
            self.Deliver_Transaction(self.transaction_list[0][3])
            #if(Transaction in self.transaction_Priority.keys()):
            #    del self.transaction_Priority[Transaction] 
            heapq.heappop(self.transaction_list)
        return

        
    def Deliver_Transaction(self,transaction):
        transaction_command = transaction.split(" ")

        if transaction_command[0] == "DEPOSIT":
            # DEPOSIT yxpqg 75 
            if transaction_command[1] in self.accounts:
                self.accounts[transaction_command[1]] += int(transaction_command[2])
            else:
                self.accounts[transaction_command[1]] = int(transaction_command[2])
            print("BALANCE ",end="", flush=True)
            for key in sorted(self.accounts.keys()):
                print(key,":",self.accounts[key],sep="",end=" ", flush=True)
            print()
        else:
            # TRANSFER yxpqg -> wqkby 13 
            if transaction_command[1] in self.accounts:
                if self.accounts[transaction_command[1]] >= int(transaction_command[4]):
                    self.accounts[transaction_command[1]] -= int(transaction_command[4])
                    if transaction_command[3] in self.accounts:
                        self.accounts[transaction_command[3]] += int(transaction_command[4])
                    else:
                        self.accounts[transaction_command[3]] = int(transaction_command[4])
                    print("BALANCE ",end="", flush=True)
                    for key in sorted(self.accounts.keys()):
                        print(key,":",self.accounts[key],sep="",end=" ", flush=True)
                    print()
            else:
                pass  


        
    