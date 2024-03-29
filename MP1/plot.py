import sys
import matplotlib.pyplot as plt
import numpy as np
max_delay_write = open("./data/max_delay.txt",mode="r")
min_delay_write = open("./data/min_delay.txt",mode="r")
avg_delay_write = open("./data/avg_delay.txt",mode="r")
bandwidth_write = open("./data/bandwidth_write.txt",mode="r")

max_data = []
min_data = []
avg_data = []
bandwidth_data = []
for line in max_delay_write:
    data_line = line.strip("\n")  # 去除首尾换行符，并按空格划分
    max_data.append(float(data_line))
for line in min_delay_write:
    data_line = line.strip("\n")  # 去除首尾换行符，并按空格划分
    min_data.append(float(data_line))
for line in avg_delay_write:
    data_line = line.strip("\n")  # 去除首尾换行符，并按空格划分
    avg_data.append(float(data_line))
for line in bandwidth_write:
    data_line = line.strip("\n")  # 去除首尾换行符，并按空格划分
    bandwidth_data.append(float(data_line))

rate_list = np.arange(0.1, 1.1, 0.1)
plt.figure()
plt.title("Rate Graph")

plt.subplot(2,2,1)
plt.xlabel("Rate")
plt.ylabel("max_delay")
plt.plot(rate_list,max_data)

plt.subplot(2,2,2)
plt.xlabel("Rate")
plt.ylabel("min_delay")
plt.plot(rate_list,min_data)

plt.subplot(2,2,3)
plt.xlabel("Rate")
plt.ylabel("avg_delay")
plt.plot(rate_list,avg_data)

plt.subplot(2,2,4)
plt.xlabel("Rate")
plt.ylabel("bandwidth")
plt.plot(rate_list,bandwidth_data)
plt.savefig(fname = "Rate graph")
plt.show()


