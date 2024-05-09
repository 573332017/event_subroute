import os
import csv
import matplotlib.pyplot as plt
from pylab import mpl
import datetime as dt
from datetime import timedelta
from dateutil import parser
from dateutil import rrule
import numpy as np
# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
Time = {} #时间映射成数字
ys_Time = {}#数字映射成时间
entity = {}
fan_entity={} #反向 数字-》实体
tri_time = {}
tri_time_merge={} #三元组按照时间区间合并
en_time_merge={}#实体按照时间区间合并
time_merge_key={}
diff_tri_pre={} #当前时间区间出现 前一时间区间未出现的三元组
diff_tri_lat={} #前一时间区间出现 当前时间区间未出现的三元组
diff_en_pre={} #当前时间区间出现 前一时间区间未出现的实体
diff_en_lat={} #前一时间区间出现 当前时间区间未出现的实体
same_tri={}
same_en={}
TMP_NAME = "亲美反共"
PATH = f"国际政治事件_100_txt/{TMP_NAME}/"
PATH_EXT=f"国际政治事件_frequency_10/{TMP_NAME}/"
FILE = f"{TMP_NAME}_30days.csv"
TIME_GRANULARITY = 7

def read_csv(in_file):
    '''
    读取文件
    '''
    en_num=0
    time_num=0
    with open(in_file,'r', encoding='utf-8') as file:
        reader=csv.reader(file)
        for elements in reader:
            #elements = line.strip().split(",")
            if(len(elements)>6) :continue

            tri_time.setdefault(elements[5], set()).add((elements[0], elements[2],elements[3])) #[时间]：（头 关系 尾）

            #将实体 映射成数字 便于画图
            if (entity.get(elements[0]) == None):
                entity[elements[0]] = en_num
                fan_entity[en_num] = elements[0]
                en_num += 1
            if (entity.get(elements[3]) == None):
                entity[elements[3]] = en_num
                fan_entity[en_num] = elements[3]
                en_num += 1

        #将时间映射成数字 便于画图
        for i in sorted(tri_time.keys()):
            time_num += 1
            Time[i]=time_num
            ys_Time[time_num]=i
        # #补全第一个时间
        # second_time = dt.datetime.strptime(ys_Time[1], "%Y-%m-%d").date()
        # ys_Time[0] = (second_time + dt.timedelta(days=-1)).strftime('%Y-%m-%d')
        # Time[ys_Time[0]] = 0

def get_diff():
    #计算区间个数
    # range_cnt=len(tri_time.keys())//TIME_GRANULARITY +1
    range_cnt=1
    #按照Time_G 来合并区间到tri_time_merge
    start_time=dt.datetime.strptime(ys_Time[1], "%Y-%m-%d").date()
    end_time=start_time + dt.timedelta(days=TIME_GRANULARITY-1)
    tri_time_merge[range_cnt] = {}
    en_time_merge[range_cnt] = {}
    time_merge_key[range_cnt]=[start_time.strftime("%Y-%m-%d"),end_time.strftime("%Y-%m-%d")]
    for t in Time.keys():
        now_time=dt.datetime.strptime(t, "%Y-%m-%d").date()
        #当前时间不在区间范围内 ，新开一个区间
        if now_time >end_time:
            start_time = now_time
            end_time = start_time + dt.timedelta(days=TIME_GRANULARITY-1)
            range_cnt+=1
            tri_time_merge[range_cnt] = {}
            en_time_merge[range_cnt] = {}
            time_merge_key[range_cnt]=[start_time.strftime("%Y-%m-%d"),end_time.strftime("%Y-%m-%d")]
        # 遍历当前时间内的三元组
        for item in tri_time[t]:
            # 统计每个出现过的实体 的出现次数
            try:
                en_time_merge[range_cnt][item[0]] += 1
            except KeyError:
                en_time_merge[range_cnt][item[0]] = 1
            try:
                en_time_merge[range_cnt][item[2]] += 1
            except KeyError:
                en_time_merge[range_cnt][item[2]] = 1
            # 统计每个出现过的三元组 的出现次数
            try:
                tri_time_merge[range_cnt][item] += 1
            except KeyError:
                tri_time_merge[range_cnt][item] = 1


    #比较每个区间与前后区间 实体、三元组的不同
    for i in range(1,range_cnt+1):
        flag1=False
        flag2=False
        #如果前后区间存在 则创建一个list 存储差异三元组 or 实体
        if i-1>=1 and (dt.datetime.strptime(time_merge_key[i][0], "%Y-%m-%d").date()-dt.datetime.strptime(time_merge_key[i-1][1], "%Y-%m-%d").date()).days<2:
            flag1= True
            diff_en_pre[i]=[]
            diff_tri_pre[i]=[]
            same_tri[i]=[]
            same_en[i]=[]
        if i+1<=range_cnt and (dt.datetime.strptime(time_merge_key[i+1][0], "%Y-%m-%d").date()-dt.datetime.strptime(time_merge_key[i][1], "%Y-%m-%d").date()).days<2:
            flag2=True
            diff_tri_lat[i]=[]
            diff_en_lat[i]=[]
        #三元组
        for triple in tri_time_merge[i].keys():
            # 在当前区间 不在前一区间
            if flag1:
                # 在当前区间 不在前一区间
                if triple not in tri_time_merge[i-1].keys():
                    diff_tri_pre[i].append([triple,tri_time_merge[i][triple]]) # [三元组，出现次数]
                # 同时出现
                else:
                    same_tri[i].append([triple, tri_time_merge[i-1][triple],tri_time_merge[i][triple]])  #[三元组,前一区间出现次数 当前区间出现次数]

            if flag2 :
                # 在当前区间 不在后一区间
                if triple not in tri_time_merge[i+1].keys():
                    diff_tri_lat[i].append([triple,tri_time_merge[i][triple]]) # [三元组，出现次数]
        #实体
        for entity in en_time_merge[i].keys():
            # 在当前区间 不在前一区间
            if flag1:
                # 在当前区间 不在前一区间
                if entity not in en_time_merge[i - 1].keys():
                    diff_en_pre[i].append([entity, en_time_merge[i][entity]])  # [实体，出现次数]
                # 同时出现
                else:
                    same_en[i].append([entity, en_time_merge[i-1][entity],en_time_merge[i][entity]]) #[实体,前一区间出现次数 当前区间出现次数]

            if flag2:
                # 在当前区间 不在后一区间
                if entity not in en_time_merge[i + 1].keys():
                    diff_en_lat[i].append([entity, en_time_merge[i][entity]])  # [三元组，出现次数]

def output_txt():
    with open(PATH + 'diff_tri_pre.txt', 'w', encoding='utf-8') as output_file:
        #存储当前区间存在 前一区间不存在的三元组
        for i in diff_tri_pre.keys():
            output_file.write(f"当前区间：{time_merge_key[i][0]} ~ {time_merge_key[i][1]} 前一区间：{time_merge_key[i-1][0]} ~ {time_merge_key[i-1][1]}  \n")
            for item in diff_tri_pre[i]:
                output_file.write(f"{item[0]} 出现次数： {item[1]}  \n")
            output_file.write(f"\n")

    with open(PATH + 'diff_tri_lat.txt', 'w', encoding='utf-8') as output_file:
        # 存储当前区间存在 后一区间不存在的三元组
        for i in diff_tri_lat.keys():
            output_file.write(f"当前区间：{time_merge_key[i][0]} ~ {time_merge_key[i][1]} 后一区间：{time_merge_key[i+1][0]} ~ {time_merge_key[i+1][1]}  \n")
            for item in diff_tri_lat[i]:
                output_file.write(f"{item[0]} 出现次数： {item[1]}  \n")
            output_file.write(f"\n")

    with open(PATH + 'same_tri.txt', 'w', encoding='utf-8') as output_file:
        # 存储当前区间和前一区间都存在的三元组
        for i in same_tri.keys():
            output_file.write(f"当前区间：{time_merge_key[i][0]} ~ {time_merge_key[i][1]} 前一区间：{time_merge_key[i-1][0]} ~ {time_merge_key[i-1][1]}  \n")
            for item in same_tri[i]:
                output_file.write(f"{item[0]} 出现次数： {item[1]}  \n")
            output_file.write(f"\n")

    with open(PATH + 'diff_en_pre.txt', 'w', encoding='utf-8') as output_file:
        # 存储当前区间存在 前一区间不存在的实体
        for i in diff_en_pre.keys():
            output_file.write(f"当前区间：{time_merge_key[i][0]} ~ {time_merge_key[i][1]} 前一区间：{time_merge_key[i-1][0]} ~ {time_merge_key[i-1][1]}  \n")
            for item in diff_en_pre[i]:
                output_file.write(f"{item[0]} 出现次数： {item[1]}  \n")
            output_file.write(f"\n")

    with open(PATH + 'diff_en_lat.txt', 'w', encoding='utf-8') as output_file:
        # 存储当前区间存在 后一区间不存在的实体
        for i in diff_en_lat.keys():
            output_file.write(f"当前区间：{time_merge_key[i][0]} ~ {time_merge_key[i][1]} 后一区间：{time_merge_key[i+1][0]} ~ {time_merge_key[i+1][1]}  \n")
            for item in diff_en_lat[i]:
                output_file.write(f"{item[0]} 出现次数： {item[1]}  \n")
            output_file.write(f"\n")

    with open(PATH + 'same_en.txt', 'w', encoding='utf-8') as output_file:
        # 存储当前区间和前一区间都存在的实体
        for i in same_tri.keys():
            output_file.write(f"当前区间：{time_merge_key[i][0]} ~ {time_merge_key[i][1]} 前一区间：{time_merge_key[i-1][0]} ~ {time_merge_key[i-1][1]}  \n")
            for item in same_tri[i]:
                output_file.write(f"{item[0]} 出现次数： {item[1]}  \n")
            output_file.write(f"\n")



if __name__ == '__main__':
    read_csv(PATH + FILE)
    get_diff()
    output_txt()