import socket
import threading
import time
import json
import heapq
#需要自己收信息的Port
#需要要连接的Node的IP和Port
class Basic_Node:
    def __init__(self,Port):
        #实例变量都在函数里定义
        #self.Init_Server(Port)
        #thd = threading.Thread(target=Basic_Node.Init_Server, args=(self,Port))#main_thread在持续accept接受(如果没有 就卡住)，new_thread进行信息分析
        #thd.start()
        self.Send_dict = {}
        self.Send_socket_list = []#用来给别的Node发送信息
        self.Connect_num = 0
        return
#作为Server
    def Init_Server(self,Port):
        self.Server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.Server_socket.bind(("", Port))
        print("我开始听了！")
        self.Server_socket.listen(30)   
        #多线程进行收消息，每个线程都一直不出来，直到连接结束
        while True:
            Clients_socket, _ = self.Server_socket.accept() #return 别的node的套接字对象和address 会一直阻塞在这里！
            self.Connect_num = self.Connect_num+1
            print("有人来啦！")
            thd = threading.Thread(target=Basic_Node.handle_message, args=(self,Clients_socket))#main_thread在持续accept接受(如果没有 就卡住)，new_thread进行信息分析
            thd.start()
            #thd.join()#不需要join
    #处理收到的msg
    def handle_message(self,Clients_socket):
        #处理收到的transaction
        while True:
            recv_data  = Clients_socket.recv(4096)
            if(recv_data):
                message = recv_data.decode()#.split()
                """ msg_list = json.loads(message)
                self.divide_message(msg_list) """
                #msg_list = json.loads(message)
                #print("A new Transaction!")
                print(message)
#连接别的Node            
    def Connect_to_Servers(self,Name, Port,IP = "127.0.0.1"):#client是为了给别的servers发送信息，都是平等的，因为每次都是群发
        if(IP == "localhost"):
            IP = "127.0.0.1"
        Port = int(Port)
        Send_socket = socket.socket()
        print("Try to Connect to :", IP, Port)
        while True:
            try:
                Send_socket.connect((IP,Port))
                break
            except:
                #如果不成功 持续重连
                print("ReConnect to Port:", Port)
                time.sleep(3)
                pass
        print("Connect Successful!") 
        self.Send_dict[Name] = Send_socket
        self.Send_socket_list.append(Send_socket)
        return
    
#群发list
    def Send_msg(self, msg_list):
        #print("Send message: ", msg_list)
        if len(msg_list) == 0:
            print("Msg is empty!")
            return
        msg = json.dumps(msg_list)
        for socket_fd in self.Send_socket_list:
            socket_fd.send(msg.encode('utf-8'))
        return

#给单个Node发list  
    def Send_1to1_msg(self,socket_fd, msg_list):
        if len(msg_list) == 0:
            print("Msg is empty!")
            return
        msg = json.dumps(msg_list)
        socket_fd.send(msg.encode('utf-8'))
        return


