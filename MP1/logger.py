import socket
import sys
import threading
import time

min_delay = 100 # 最小的delay
max_delay = 0 #最大的delay
total_num = 0 #信息的总个数
total_delay = 0 #总共的delay
total_word = 0 #总共的字节长度
mutex = threading.Lock() 
def handle_message(tcp_node, task):
    global min_delay 
    global max_delay 
    global total_num 
    global total_delay 
    global total_word 
    connected = False
    while True:
        recv_data = tcp_node.recv(4096)
        if recv_data:
            message = recv_data.decode().split()
            print(message)
            # print(recv_data.decode())
            # print(message)
            # tcp_node.send(message[1].encode(encoding='utf-8'))

            if len(message[1]) != 64:  # The length of message is 64
                # receive node name
                if not connected:
                    node_name = message[1]
                    connected = True
                    print(message[0], "-", node_name, "connected")
                    print(threading.active_count())
                else:
                    print(message[0], "-", node_name, "disconnected")
                    print(threading.active_count())
                    tcp_node.close()
                    break
            else:
                # receive message
                if task == 1:
                    # print log file
                    pass
                    #print(message[0], node_name)
                    #print(message[1])
                else:
                    # print evaluation file
                    delay = time.time()-float(message[0])
                    mutex.acquire()
                    max_delay = max(delay,max_delay)
                    min_delay = min(delay,min_delay)
                    total_num = total_num+1
                    total_delay = total_delay+delay
                    #print(float(message[0]),time.time(),delay)
                    total_word  = total_word+len(recv_data)
                    mutex.release()
                    bandwidth = len(recv_data)/delay
                    #in task2, i need to remember all the delay and the bandwith, draw a graph with the relationship
                    #with the sending rate.
                    # so write csv file for each sending rate and draw graph for each rate.
                    print(node_name, ",", delay, ',', bandwidth)

        else:
            print("Never go to this place!!")
            tcp_node.close()
            break

def save_data():
    print("SAVE DATA!!!!!")
    global min_delay 
    global max_delay 
    global total_num 
    global total_delay 
    global total_word 
    print("From MAX to MIN", max_delay,min_delay,min_delay, total_delay, total_num, total_word)
    
    max_delay_write = open("./data/max_delay.txt",mode="a+")
    min_delay_write = open("./data/min_delay.txt",mode="a+")
    avg_delay_write = open("./data/avg_delay.txt",mode="a+")
    bandwidth_write = open("./data/bandwidth_write.txt",mode="a+")

    max_delay_write.write("\n"+str(max_delay))
    min_delay_write.write("\n"+str(min_delay))
    avg_delay_write.write("\n"+str(total_delay/total_num))
    bandwidth_write.write("\n"+str(total_word/total_delay))
    max_delay_write.close
    min_delay_write.close
    avg_delay_write.close
    bandwidth_write.close

def main():
    global nodes_num
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 1234  # default port

    if len(sys.argv) > 2:
        task = int(sys.argv[2])
    else:
        task = 1

    tcp_logger = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    tcp_logger.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    tcp_logger.bind(("", port))

    tcp_logger.listen(24)   
    
    while True:
        if(task==2 and threading.active_count()==4):#task2的情况下且已经完成了额外的3个连接 停止accept，跳出循环
            break
        tcp_node, _ = tcp_logger.accept() 
        thd = threading.Thread(target=handle_message, args=(tcp_node, task))#main_thread在持续accept接受(如果没有 就卡住)，new_thread进行信息分析
        thd.start()
    if(task == 2):
        while(threading.active_count()>1):
            time.sleep(1)
        # when only main thread exist, write the data to the text.
        save_data()
    else:#task1 是不会到这里的。
        tcp_logger.close()


if __name__ == '__main__':
    main()
