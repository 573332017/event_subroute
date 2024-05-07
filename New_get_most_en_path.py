'''
该程序直接读取子图，并按照节点出现频率筛选并绘制路径
'''
import json
import csv
import os
import matplotlib.pyplot as plt
from pylab import mpl
import datetime as dt
from datetime import timedelta
from dateutil import parser
from dateutil import rrule
import numpy as np
import time

# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
# N = 500000
Time = {} #时间映射成数字
ys_Time = {}#数字映射成时间
zitu = []
TT=[]
sorted_T=[]
entity = {}
fan_entity={} #反向 数字-》实体
zitu_path=[]#子图路径按路径输出
#Path=set()#子图路径按边输出
Path={}
# edges = [[] for _ in range(N)]#总图的所有边
edges = {}
#子图下某时间存在的三元组
# tri_time=[set() for _ in range(N)]
tri_time = {}
ext_tri_time={}  #师兄新发的三元组 按照时间索引存储
ext_tri_time_g={}
fig, ax = plt.subplots(dpi=150, figsize=(24, 32))
# 统计该子图下每个实体出现的数量
zitu_entity = {}
# 子图下某个实体映射成的数字
ys_en = {}
edge_has_path={}
judge_edge_back={}
y_list=[]
y_label=[]
value_time=set() #有效时间
cnt=0
spec_path=set()
ext_Path=set()   #存储师兄新给的以时间命名的csv 所有路径下的三元组
ext_Path_g=set() #存储师兄新给的以graphx命名的csv 所有路径下的三元组

TMP_NAME = "反美猪公投"
PATH = f"国际政治事件_frequency_10/{TMP_NAME}/"
PATH_EXT=f"国际政治事件_frequency_10/{TMP_NAME}/"
FILE = "反美猪公投_30days.csv"
EVENT_NAME = "反莱猪公投"
AIM_NAME= "反莱猪公投"
ENT_NUM = 40
FOCUS_ENT = "反莱猪公投"
TIME_GRANULARITY = 5 # 时间粒度控制
ROUTE_LEN = 2 # 路径长度控制，过滤小于该长度的路径

# 设定读取的三元组时间范围，因为有些事件的时间跨度较大，不便展示
S_TIME = '1000-01-01' # 不限时间范围
E_TIME = '3000-01-01'
MAX_RANGE=20 #设定画图时某边出现次数上限 如果次数超过max就设定为max max时即为红色
# S_TIME = '2017-01-01'
# E_TIME = '2023-01-01'

FOCUS_ENT_LIST = ['特朗普', '德国媒体', '美国官员', '中国', '美国国会',
'俄罗斯', '美国', '中国大陆', '蔡英文', '习近平', '网络强国建设', '金正恩',
'中俄关系', '乌克兰', '唐纳德·特朗普']

# FOCUS_ENT_LIST = ['美国政府', '中国企业', '美国', '中国', '世界卫生组织', '小约翰·柯布', '吴部长',
#  '台湾', '蔡英文总统', '民进党', '蔡英文', '马英九', '北京', '中共', '朝鲜战争']

def draw_lines_from_file(path,s_path,ext_path,flag,col):
    '''
    绘图函数
    '''
    if focus_entity not in ys_en:
        print(f"以{TIME_GRANULARITY}天为关联时间下不存在 {FOCUS_ENT} 实体,请调整关联时间范围")
        return
    # 初始化空列表来存储坐标点
    points = []
    label_list = []
    v_time = list(value_time)
    try:
        start_time = dt.datetime.strptime(ys_Time[v_time[0]], "%Y-%m-%d").date()
    except:
        print("时间粒度太小，路径为空")
        return
    weights = np.linspace(0.2, 1, MAX_RANGE)  # 权重值，范围从 0 到 1
    # 设置颜色映射
    cmap = plt.cm.get_cmap('coolwarm')
    end_time = dt.datetime.strptime(ys_Time[v_time[len(v_time) - 1]], "%Y-%m-%d").date()
    Months = rrule.rrule(rrule.MONTHLY, dtstart=start_time, until=end_time).count()
    for i in range(0, Months + 1, 1):
        label_list.append((start_time + timedelta(days=30) * i).strftime("%Y-%m"))
    plt.xticks(range(0, (len(label_list) - 1) * 30 + 5, 30), label_list)

    l = 0
    r = rrule.rrule(rrule.DAILY, dtstart=start_time, until=end_time).count()
    plt.plot([l, r], [ys_en[event_id], ys_en[event_id]], c='orange', linestyle='--')
    plt.yticks(list(y_list), y_label)
    plt.title(TMP_NAME + "_frequency_" + str(ys_en[event_id]) + '_' + str(TIME_GRANULARITY))

    # 读取文件并解析每行数据
    for item in path.keys():
        # 将两个点作为一个元组添加到列表中
        date1 = (dt.datetime.strptime(ys_Time[item[0]], "%Y-%m-%d").date() - start_time).days
        date2 = (dt.datetime.strptime(ys_Time[item[2]], "%Y-%m-%d").date() - start_time).days
        points.append([(date1, item[1]), (date2, item[3]),path[item]])
    for values in y_list:
        # 普通节点不再通过虚线标识，只标识目标事件实体和关注的实体
        if (values == ys_en[event_id]):
            plt.plot([l, r], [values, values], c='red', linestyle='--')
        elif (values == ys_en[aim_id]):
            plt.plot([l, r], [values, values], c='black', linestyle='--')
        # elif (values == ys_en[focus_entity]):
        #     plt.plot([l, r], [values, values], c='green', linestyle='--')
        # elif (values in [ys_en[e] for e in focus_entity_list if e in ys_en.keys()]):
        #     plt.plot([l, r], [values, values], c='black', linestyle='--')

    # 遍历所有点对，绘制线条
    for point_pair in points:

        if point_pair[2] >= MAX_RANGE: point_pair[2] = MAX_RANGE-1
        ax.plot([point_pair[0][0], point_pair[1][0]],
                [point_pair[0][1], point_pair[1][1]], color = cmap(weights[point_pair[2]]))
        # plt.draw()
        # plt.pause(0.01)
        plt.scatter(point_pair[0][0], point_pair[0][1], s=10, marker='o', c='red')
        plt.scatter(point_pair[1][0], point_pair[1][1], s=10, marker='o', c='red')

    # 有关focus_entity的路径
    # spec_points = []
    # for item in s_path:
    #     # 将两个点作为一个元组添加到列表中
    #     # if (zitu_entity[item[1]] >= 3 and zitu_entity[item[3]] >= 3):  # 路径中该结点出现次数小于3 就滤掉
    #     date1 = (dt.datetime.strptime(ys_Time[item[0]], "%Y-%m-%d").date() - start_time).days
    #     date2 = (dt.datetime.strptime(ys_Time[item[2]], "%Y-%m-%d").date() - start_time).days
    #     spec_points.append(((date1, item[1]), (date2, item[3])))
    #     # spec_points.append(((item[0], ys_en[item[1]]), (item[2], ys_en[item[3]])))
    # for point_pair in spec_points:
    #     ax.plot([point_pair[0][0], point_pair[1][0]],
    #             [point_pair[0][1], point_pair[1][1]], "r")

    # 在师兄新给的三元组中出现过的路径
    ext_points = []
    # for item in ext_path:
    #     # 将两个点作为一个元组添加到列表中
    #     # if (zitu_entity[item[1]] >= 3 and zitu_entity[item[3]] >= 3):  # 路径中该结点出现次数小于3 就滤掉
    #     date1 = (dt.datetime.strptime(ys_Time[item[0]], "%Y-%m-%d").date() - start_time).days
    #     date2 = (dt.datetime.strptime(ys_Time[item[2]], "%Y-%m-%d").date() - start_time).days
    #     ext_points.append(((date1, item[1]), (date2, item[3])))
    #     # spec_points.append(((item[0], ys_en[item[1]]), (item[2], ys_en[item[3]])))
    # for point_pair in ext_points:
    #     ax.plot([point_pair[0][0], point_pair[1][0]],
    #             [point_pair[0][1], point_pair[1][1]], "green")
    plt.savefig(f'{PATH}{TMP_NAME}_frequency_eventid{str(ys_en[event_id])}_{S_TIME}_{E_TIME}_time{str(TIME_GRANULARITY)}_{flag}.png')
    print(f"路径绘制完成，保存为{PATH}{TMP_NAME}_frequency_eventid{str(ys_en[event_id])}_{S_TIME}_{E_TIME}_time{str(TIME_GRANULARITY)}_{flag}.png")
    # plt.show()


def find_paths_back(current_time, current_edge, path,size):
    '''
    寻找后向路径
    '''
    path.append(current_edge)
    global cnt
    current_en = current_edge[3]
    next_edges=[]
    now_time=ys_Time[current_time]
    date1 = dt.datetime.strptime(now_time, "%Y-%m-%d").date()  ##datetime.date(2018, 1, 6)
    #如果存在日期相差小于要求 且头尾对应的边 就加入到next_edges[]内
    for i in range(1,size+1,1):
        if current_time+i  not in ys_Time:continue
        next_time=ys_Time[current_time+i]
        date2 = dt.datetime.strptime(next_time, "%Y-%m-%d").date()  ##datetime.date(2018, 1, 9)
        # （2）计算两个日期date的天数差
        Days = (date2 - date1).days
        if(Days>size): continue; #日期相差超过要求 就不考虑

        if current_time+i in tri_time.keys(): #如果时间点内存在三元组才进一步处理
            for t in tri_time[current_time+i]:
                if current_en==t[0]:
                    next_edges.append((current_time,t[0],current_time+i,t[1]))


    if len(next_edges) > 0:
        for next_edge in next_edges:
            if judge_edge_back.get(next_edge) == None:  # 这条边没有考虑过路径
                find_paths_back(next_edge[2], next_edge, path,size)
                judge_edge_back[next_edge] = True
            else:
                path.append(next_edge)

    # 按照边的形式输出
    if len(path) >= ROUTE_LEN:
        for edge in path:
            try:
                # 尝试对键为 edge 的值进行递增操作
                Path[edge] += 1
            except KeyError:
                # 键不存在时的处理逻辑
                Path[edge] = 1
            #Path.add(edge)
            value_time.add(edge[0])
            value_time.add(edge[2])

            if edge[2] in ext_tri_time.keys():
                tmp = ext_tri_time[edge[2]]
                if (edge[1], edge[3]) in tmp:
                    ext_Path.add(edge)

            if edge[2] in ext_tri_time_g.keys():
                tmp = ext_tri_time_g[edge[2]]
                if (edge[1], edge[3]) in tmp:
                    ext_Path_g.add(edge)

        cnt += 1
    path.pop()

def find_paths(edges, current_edge, path):
    '''
    找有关focus_entity的路径
    '''
    path.append(current_edge)
    current_x = current_edge[2]
    current_y = current_edge[3]

    next_edges = [edge for edge in edges if edge[0] == current_x and edge[1] == current_y]
    if len(next_edges) > 0:
        for next_edge in next_edges:
            if(edge_has_path.get(next_edge)==None): #这条边的路径还没有找过
                find_paths(edges, next_edge, path)
                edge_has_path[next_edge]=True
            else:
                path.append(next_edge)
    #按照路径形式输出 json要求
    # if len(path) >= 2:
    #     Path = []
    #     for edge in path:
    #         Path.append(ys_Time[edge[0]]),Path.append(edge[1])
    #         #print(f"({edge[0]} {edge[1]} {edge[2]} {edge[3]}) ->", end=" ")
    #     Path.append(ys_Time[edge[2]]),Path.append(edge[3])
    #     zitu_path.append(Path)

    #按照边的形式输出
    flag=False
    if len(path) >= ROUTE_LEN:
        for edge in path:
            if ((edge[1] == ys_en[focus_entity]) or (edges[3] == ys_en[focus_entity])):  # 如果该路径中包含蔡英文实体
                flag = True

        if (flag == True):
            for edge in path:
                spec_path.add(edge)  # 将该路径加入到特殊画线的spec_path中


    path.pop()

def get_path(size):
    '''
    获得当前num个实体的子图下的路径
    '''
    for edge in F_zitu:
        path = []
        find_paths_back(edge[2],edge,path,size)
        # 找与focus_entity有关的路径 因为暂时不需要 所以注释掉
        # l_path = list(Path.keys())
        # for edge in l_path:
        #     s_path = []
        #     find_paths(l_path, edge, s_path)

def get_zitu_time(id):
    '''
    获得所有出现过的时间的映射 以及按照时间从前到后 且去重后的图
    '''
    time_num = 1
    for res in sorted_T:
        pre_time=(dt.datetime.strptime(res[2], "%Y-%m-%d").date() + dt.timedelta(days=-1)).strftime('%Y-%m-%d')
        if pre_time not in Time:
            time_num += 1
            ys_Time[time_num] = pre_time
            Time[pre_time] = time_num

        if res[2] not in Time:
            time_num += 1
            ys_Time[time_num] = res[2]
            Time[res[2]] = time_num
        a = int(res[0])
        b = int(res[1])

        edges.setdefault(a, []).append((b, 0, res[2]))
        edges.setdefault(b, []).append((a, 1, res[2]))
        zitu.append([Time[res[2]] - 1, a, Time[res[2]], b])
    # 举例: second_time=2020-01-01  ys_time[1]=2019-12-31
    second_time = dt.datetime.strptime(ys_Time[2], "%Y-%m-%d").date()
    ys_Time[1] = (second_time + dt.timedelta(days=-1)).strftime('%Y-%m-%d')
    Time[ys_Time[1]] = 1

    #子图id
    # item = id
    # for i in edges[item]:
    #     if not i[1]: #item头实体
    #         zitu.append([Time[i[2]]-1,item, Time[i[2]],i[0] ])
    #     else:
    #         zitu.append([Time[i[2]]-1,i[0],Time[i[2]],item ])
    #      # 统计该子图下每个实体出现的数量
    #     for j in edges[i[0]]:
    #         if not j[1]: #i[0] 作为头实体
    #             zitu.append([Time[j[2]]-1,i[0], Time[j[2]],j[0]])
    #         else:
    #             zitu.append([Time[j[2]]-1,j[0],Time[j[2]],i[0]])
    unique_zitu = list(set(map(tuple, zitu)))
    sorted_zitu =sorted(unique_zitu, key=lambda x: x[0])
    return sorted_zitu

def filt_zitu(num):
    '''
    在此添加函数说明
    '''
    for item in sorted_zitu:
        zitu_entity[item[1]] = zitu_entity.get(item[1], 0) + 1
        zitu_entity[item[3]] = zitu_entity.get(item[3], 0) + 1
    sorted_en = sorted(zitu_entity.items(), key=lambda x: x[1], reverse=True)

    # 将出现最多的实体编号映射到中间
    l = 0
    r = len(sorted_en)
    num_en=[]
    if (r % 2):  # 总数为奇数
        mid = r // 2  # 取整
        ys_en[sorted_en[l][0]] = mid
        num_en.append(sorted_en[l][0])
        l += 1
        for i in range(1, mid + 1):
            ys_en[sorted_en[l][0]] = mid - i
            num_en.append(sorted_en[l][0])
            l += 1
            ys_en[sorted_en[l][0]] = mid + i
            num_en.append(sorted_en[l][0])
            l += 1
            if (l >= num): break
    else:
        mid1 = r // 2
        mid2 = mid1 - 1
        for i in range(mid1):
            ys_en[sorted_en[l][0]] = mid1 + i
            num_en.append(sorted_en[l][0])
            l += 1
            ys_en[sorted_en[l][0]] = mid2 - i
            num_en.append(sorted_en[l][0])
            l += 1
            if (l >= num): break

    down = 0
    up = 1e5
    if num < 1e7:
        num //= 2
        down = r // 2 - num
        up = r // 2 + num
    F_zitu = []
     # 事件实体不在出现最多的num个实体内 事件实体重新映射
    ext = 0
    if (event_id not in num_en):
        while (up + ext in ys_en.values()):
            ext+=1
        ys_en[event_id] = up + ext
        num_en.append(event_id)

        # 把一跳子图的涉及的所有实体加入映射中
        if (num <= 1e7):
            # 实体重新映射
            for i in edges[event_id]:
                if (i[0] not in num_en):
                    while (up + ext in ys_en.values()):
                        ext += 1
                    ys_en[i[0]] = up + ext
                    num_en.append(i[0])
                    # 一跳子图的所有边直接加入路径中
                if not i[1]:  # event作为头实体
                    try:
                        # 尝试对键为 edge 的值进行递增操作
                        Path[(Time[i[2]] - 1, ys_en[event_id], Time[i[2]], ys_en[i[0]])] += 1
                    except KeyError:
                        # 键不存在时的处理逻辑
                        Path[(Time[i[2]] - 1, ys_en[event_id], Time[i[2]], ys_en[i[0]])] = 1
                    #Path.add((Time[i[2]] - 1, ys_en[event_id], Time[i[2]], ys_en[i[0]]))
                else:
                    try:
                        # 尝试对键为 edge 的值进行递增操作
                        Path[(Time[i[2]] - 1, ys_en[i[0]], Time[i[2]], ys_en[event_id])] += 1
                    except KeyError:
                        # 键不存在时的处理逻辑
                        Path[(Time[i[2]] - 1, ys_en[i[0]], Time[i[2]], ys_en[event_id])] = 1
                    #Path.add((Time[i[2]] - 1, ys_en[i[0]], Time[i[2]], ys_en[event_id]))

    # 目标实体不在出现最多的num个实体内 目标实体重新映射
    if (aim_id not in num_en):
        while (up + ext in ys_en.values()):
            ext += 1
        ys_en[aim_id] = up + ext
        num_en.append(aim_id)

    #print(ys_en[event_id],zitu_entity[event_id])
    #取出现次数最多的num个元素构成的子图

    with open(PATH + 'ys_node_mapping.txt', 'w',encoding='utf-8') as output_file:
        for i in num_en:
            output_file.write(f"{fan_entity[i]}  映射为： {ys_en[i]} 出现次数：{zitu_entity[i]} \n")
            # if(ys_en[i]>=down and ys_en[i[0]]<=up):
            y_list.append(ys_en[i])
            y_label.append(fan_entity[i])

    for item in sorted_zitu:
        if item[1] not in ys_en or item[3] not in ys_en: continue
        a=ys_en[item[1]]
        b=ys_en[item[3]]  #统计每个三元组的头尾实体映射id
        #if((a>=down and a<=up and b>=down and b<=up) or num>1e7):
        F_zitu.append((item[0],a,item[2],b))
        # tri_time[item[2]].add((a, b))
        tri_time.setdefault(item[2],set()).add((a, b))

    return F_zitu


def last_element_sort(elem):
    '''
    列表按照最后一个元素排序
    '''
    return elem[-1]

def read_txt(in_file):
    '''
    读取文件
    '''
    triple=[]
    en_num=0
    # with open("time.txt", 'w', encoding='utf-8') as output_file:
    with open(in_file,'r', encoding='utf-8') as file:
        for line in file:
            elements = line.strip().split()
            #实体映射成数字

            if(entity.get(elements[0])==None):
                entity[elements[0]]=en_num
                fan_entity[en_num]=elements[0]
                en_num+=1
            if (entity.get(elements[3]) == None):
                entity[elements[3]] = en_num
                fan_entity[en_num]=elements[3]
                en_num += 1
            triple.append([entity[elements[0]], entity[elements[3]], elements[5]])

    unique_tri =list(set(map(tuple, triple)))
    sorted_tri = sorted(unique_tri, key=last_element_sort)
    return sorted_tri
def read_csv(in_file):
    '''
    读取文件
    '''
    triple=[]
    en_num=0
    with open(in_file,'r', encoding='utf-8') as file:
        reader=csv.reader(file)
        for elements in reader:
            #elements = line.strip().split(",")
            if(len(elements)>6) :continue
            if (entity.get(elements[0]) == None):
                entity[elements[0]] = en_num
                fan_entity[en_num] = elements[0]
                en_num += 1
            if (entity.get(elements[3]) == None):
                entity[elements[3]] = en_num
                fan_entity[en_num] = elements[3]
                en_num += 1
            
            time_data = dt.datetime.strptime(elements[5], "%Y-%m-%d").date()
            if time_data >= dt.datetime.strptime(S_TIME, "%Y-%m-%d").date() and time_data <= dt.datetime.strptime(E_TIME, "%Y-%m-%d").date():
                triple.append([entity[elements[0]], entity[elements[3]], elements[5]])

    unique_tri =list(set(map(tuple, triple)))
    sorted_tri = sorted(unique_tri, key=last_element_sort)
    return sorted_tri

def get_ext():
    # 遍历文件夹中的所有文件
    for file_name in os.listdir(PATH_EXT):
        if file_name.endswith('.csv') and not file_name.startswith('graph'):
            # 构建CSV文件的完整路径
            file_path = os.path.join(PATH_EXT, file_name)

            # 打开CSV文件
            with open(file_path, 'r', encoding='utf-8') as file:
                # 创建CSV读取器
                reader = csv.reader(file)

                # 遍历每一行并输出
                for row in reader:
                    if row[0] in entity.keys() and row[3] in entity.keys():
                        if entity[row[0]] not in ys_en or entity[row[3]] not in ys_en: continue
                        if row[5] in Time.keys():
                            ext_tri_time.setdefault(Time[row[5]],set()).add((ys_en[entity[row[0]]], ys_en[entity[row[3]]]))

        if file_name.endswith('.csv') and file_name.startswith('graph'):
            # 构建CSV文件的完整路径
            file_path = os.path.join(PATH_EXT, file_name)

            # 打开CSV文件
            with open(file_path, 'r', encoding='utf-8') as file:
                # 创建CSV读取器
                reader = csv.reader(file)

                # 遍历每一行并输出
                for row in reader:
                    if row[0] in entity.keys() and row[3] in entity.keys():
                        if entity[row[0]] not in ys_en or entity[row[3]] not in ys_en: continue
                        a = ys_en[entity[row[0]]]
                        b = ys_en[entity[row[3]]]  # 统计每个三元组的头尾实体映射id
                        if row[5] in Time.keys():
                            ext_tri_time_g.setdefault(Time[row[5]],set()).add((a, b))


if __name__ == '__main__':

    #sorted_T = read_txt(PATH + FILE)
    sorted_T = read_csv(PATH + FILE)
    event_id = entity[EVENT_NAME]
    aim_id=entity[AIM_NAME]
    # sorted_zitu=get_zitu(event_id)
    sorted_zitu = get_zitu_time(event_id)
    F_zitu=filt_zitu(ENT_NUM) #控制子图中包含的实体数量 若输入大于1e7 则查看所有实体的路径

    focus_entity = entity[FOCUS_ENT]
    focus_entity_list = [entity[e] for e in FOCUS_ENT_LIST if e in entity.keys()]
    get_ext()
    get_path(TIME_GRANULARITY)# 获得子图路径

    # flag =0 时 考虑以时间命名的csv文件  flag=1 时考虑以graphx命名的csv文件
    draw_lines_from_file(Path,spec_path,ext_Path,0,"b")
    # draw_lines_from_file(Path, spec_path, ext_Path_g, 1, "b")
    print(f"共绘制{cnt}条路径")
