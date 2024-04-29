# 该程序为分析分段数据，按照两跳生成事件子图，并按照实体出现频率绘制路径

import json
import matplotlib.pyplot as plt
from pylab import mpl
# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
N = 500000
Time = {} #时间映射成数字
ys_Time = {}#数字映射成时间
zitu = []
TT=[]
sorted_T=[]
entity = {}
fan_entity={} #反向 数字-》实体
zitu_path=[]#子图路径按路径输出
Path=set()#子图路径按边输出
edges = [[] for _ in range(N)]#总图的所有边
edges_time = [[] for _ in range(N)]#总图的某时间的所有边
fig, ax = plt.subplots(dpi=150, figsize=(24, 24))
# 统计该子图下每个实体出现的数量
zitu_entity = {}
# 子图下某个实体映射成的数字
ys_en = {}
edge_has_path={}
y_list=[]
y_label=[]
value_time=set() #有效时间
cnt=0
spec_path=set()

PATH = "triples_zh_time/"
FILE = "triples_zh_20_23.txt"
EVENT_NAME = "《台湾关系法》"
ENT_NUM = 30
FOCUS_ENT = "蔡英文"

FOCUS_ENT_LIST = ['特朗普', '德国媒体', '美国官员', '中国', '美国国会',
'俄罗斯', '美国', '中国大陆', '蔡英文', '习近平', '网络强国建设', '金正恩',
'中俄关系', '乌克兰', '唐纳德·特朗普']

# FOCUS_ENT_LIST = ['美国政府', '中国企业', '美国', '中国', '世界卫生组织', '小约翰·柯布', '吴部长',
#  '台湾', '蔡英文总统', '民进党', '蔡英文', '马英九', '北京', '中共', '朝鲜战争']

def draw_lines_from_file(path,col):

    points = []
    label_list = []
    first_time = int(ys_Time[2][0:4])
    last_time = int(ys_Time[len(ys_Time)][0:4])
    for i in range(first_time, last_time + 1):
        label_list.append(i)
    # label_list = ["2020", "2021", "2022", "2023"]
    plt.xticks(range(0, (len(label_list) - 1) * 12 + 5, 12), label_list)

    l = 0
    r = len(Time)
    plt.plot([l, r], [ys_en[event_id], ys_en[event_id]], c='orange', linestyle='--')
    plt.yticks(list(y_list), y_label)
    plt.title(EVENT_NAME + '_' + str(ys_en[event_id]))
    # plt.savefig(event_name + '_' + str(ys_en[event_id]) + '.png')
    # 读取文件并解析每行数据
    for item in path:
        # 将两个点作为一个元组添加到列表中
        points.append(((item[0], item[1]), (item[2], item[3])))
    for values in y_list:
        if (values == ys_en[event_id]):
            plt.plot([l, r], [values, values], c='orange', linestyle='--')
        elif (values in [ys_en[e] for e in focus_entity_list if e in ys_en.keys()]):
            plt.plot([l, r], [values, values], c='red', linestyle='--')
        elif (values == ys_en[focus_entity]):
            plt.plot([l, r], [values, values], c='green', linestyle='--')
        else:
            plt.plot([l, r], [values, values], c='black', linestyle='--')
    # 遍历所有点对，绘制线条
    for point_pair in points:
        ax.plot([point_pair[0][0], point_pair[1][0]],
                [point_pair[0][1], point_pair[1][1]], col)
        # plt.draw()
        # plt.pause(0.01)
        plt.scatter(point_pair[0][0], point_pair[0][1], s=10, marker='o', c='red')
        plt.scatter(point_pair[1][0], point_pair[1][1], s=10, marker='o', c='red')

    #特殊画线的路径
    spec_points = []
    for item in spec_path:
        # 将两个点作为一个元组添加到列表中
        # if (zitu_entity[item[1]] >= 3 and zitu_entity[item[3]] >= 3):  # 路径中该结点出现次数小于3 就滤掉
        spec_points.append(((item[0], item[1]), (item[2], item[3])))
    for point_pair in spec_points:
        ax.plot([point_pair[0][0], point_pair[1][0]],
                [point_pair[0][1], point_pair[1][1]], "r")

    plt.savefig(PATH + EVENT_NAME + '_' + str(ys_en[event_id]) + '.png')
    # plt.show()



def find_paths(edges, current_edge, path):
    path.append(current_edge)

    current_x = current_edge[2]
    current_y = current_edge[3]

    next_edges = [edge for edge in edges if edge[0] == current_x and edge[1] == current_y]
    if len(next_edges) > 0:
        for next_edge in next_edges:
            if(edge_has_path.get(next_edge)==None): #这条边的路径还没有找过
                find_paths(edges, next_edge, path)
                edge_has_path[next_edge]=True;
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
    flag=False;
    if len(path) >= 2:
        for edge in path:
            if ((edge[1] == ys_en[focus_entity]) or (edges[3] == ys_en[focus_entity])):  # 如果该路径中包含蔡英文实体
                flag = True;
            Path.add(edge)
        if (flag == True):
            for edge in path:
                spec_path.add(edge)  # 将该路径加入到特殊画线的spec_path中

    path.pop()

def get_path():
    for edge in F_zitu:
        path = []
        find_paths(F_zitu, edge, path)
def get_zitu(id):

    time_num = 1

    for res in sorted_T:
        if res[2] not in Time:
            time_num += 1
            ys_Time[time_num] = res[2]
            Time[res[2]] = time_num
            x_data.append(res[2])
        a = int(res[0])
        b = int(res[1])

        edges[a].append([b, 0, res[2]])
        edges[b].append([a, 1, res[2]])

    #子图id
    item = id

    for i in edges[item]:
        if not i[1]: #item头实体
            zitu.append([Time[i[2]]-1,item, Time[i[2]],i[0] ])
        else:
            zitu.append([Time[i[2]]-1,i[0],Time[i[2]],item ])
         # 统计该子图下每个实体出现的数量
        for j in edges[i[0]]:
            if not j[1]: #i[0] 作为头实体
                zitu.append([Time[j[2]]-1,i[0], Time[j[2]],j[0]])
            else:
                zitu.append([Time[j[2]]-1,j[0],Time[j[2]],i[0]])
    unique_zitu = list(set(map(tuple, zitu)))
    sorted_zitu =sorted(unique_zitu, key=lambda x: x[0])
    return sorted_zitu
    #for ele in T:
        #outf.write(str(Time[ele.time] - 1) + ' ' + ele.head + ' ' + str(Time[ele.time]) + ' ' + ele.tail + '\n')
def get_zitu_time(id):

    time_num = 1
    for res in sorted_T:
        if res[2] not in Time:
            time_num += 1
            ys_Time[time_num] = res[2]
            Time[res[2]] = time_num
            x_data.append(res[2])
        a = int(res[0])
        b = int(res[1])

        edges[a].append([b, 0, res[2]])
        edges[b].append([a, 1, res[2]])

    second_time = ys_Time[2]  # 举例: second_time=2020-01
    if (second_time[5:7] == "01"):
        ys_Time[1] = str(int(second_time[0:4]) - 1) + "-12"
    elif (second_time[5:7] == "12" or second_time[5:7] == "11"):
        ys_Time[1] = second_time[0:5] + str(int(second_time[5:7]) - 1)
    else:
        ys_Time[1] = second_time[0:5] + "0" + str(int(second_time[5:7]) - 1)
    Time[ys_Time[1]] = 1

    #子图id
    item = id

    for i in edges[item]:
        if not i[1]: #item头实体
            zitu.append([Time[i[2]]-1,item, Time[i[2]],i[0] ])
            edges_time[Time[i[2]]-1].append([item,i[0]])
        else:
            zitu.append([Time[i[2]]-1,i[0],Time[i[2]],item ])
            edges_time[Time[i[2]]-1].append([i[0], item])
         # 统计该子图下每个实体出现的数量
        for j in edges[i[0]]:
            if not j[1]: #i[0] 作为头实体
                zitu.append([Time[j[2]]-1,i[0], Time[j[2]],j[0]])
                edges_time[Time[i[2]] - 1].append([i[0], j[0]])
            else:
                zitu.append([Time[j[2]]-1,j[0],Time[j[2]],i[0]])
                edges_time[Time[i[2]]-1].append([j[0], i[0]])
    unique_zitu = list(set(map(tuple, zitu)))
    sorted_zitu =sorted(unique_zitu, key=lambda x: x[0])
    return sorted_zitu

def filt_zitu(num):

    for item in sorted_zitu:
        zitu_entity[item[1]] = zitu_entity.get(item[1], 0) + 1
        zitu_entity[item[3]] = zitu_entity.get(item[3], 0) + 1
    sorted_en = sorted(zitu_entity.items(), key=lambda x: x[1], reverse=True)

    # 将出现最多的实体编号映射到中间
    l = 0
    r = len(sorted_en)
    if (r % 2):  # 总数为奇数
        mid = r // 2  # 取整
        ys_en[sorted_en[l][0]] = mid
        l += 1
        for i in range(1, mid + 1):
            ys_en[sorted_en[l][0]] = mid - i

            l += 1
            ys_en[sorted_en[l][0]] = mid + i
            l += 1
    else:
        mid1 = r // 2
        mid2 = mid1 - 1
        for i in range(mid1):
            ys_en[sorted_en[l][0]] = mid1 + i
            l += 1
            ys_en[sorted_en[l][0]] = mid2 - i
            l += 1

    print(ys_en[event_id],zitu_entity[event_id])
    #取出现次数最多的num个元素构成的子图
    down=0
    up=1e5
    if num<1e7:
        num//=2
        down=r//2-num
        up=r//2+num
    F_zitu=[]
    with open(PATH + 'ys_node_mapping.txt', 'w',encoding='utf-8') as output_file:
        for i in sorted_en:
            output_file.write(f"{fan_entity[i[0]]}  映射为： {ys_en[i[0]]}  出现次数：{zitu_entity[i[0]]}\n")
            if (ys_en[i[0]]>=down and ys_en[i[0]]<=up):
                y_list.append(ys_en[i[0]])
                y_label.append(fan_entity[i[0]])
    if(fan_entity[event_id] not in y_list):
        y_list.append(ys_en[event_id])
        y_label.append(fan_entity[event_id])
    for item in sorted_zitu:
        a=ys_en[item[1]]
        b=ys_en[item[3]]  #统计每个三元组的头尾实体映射id
        if((a>=down and a<=up and b>=down and b<=up) or num>1e7):
            F_zitu.append((item[0],a,item[2],b))

    # 事件不再出现最多的num个实体内 事件实体重新映射
    if (fan_entity[event_id] not in y_label):
        ys_en[event_id] = up + 1
        y_list.append(up + 1)
        y_label.append(fan_entity[event_id])
        ext = 1
        # 把一跳子图的所有边加入路径考虑中
        if (num <= 1e7):
            # 实体重新映射
            for i in edges[event_id]:
                tmp_en = ys_en[i[0]]
                if (fan_entity[i[0]] not in y_label):
                    while (down - ext in y_list):
                        ext += 1
                    y_list.append(down - ext)
                    tmp_en = down - ext
                    y_label.append(fan_entity[i[0]])
                    ext += 1
                if not i[1]:  # event作为头实体
                    F_zitu.append((Time[i[2]] - 1, up + 1, Time[i[2]], tmp_en))
                    Path.add((Time[i[2]] - 1, up + 1, Time[i[2]], tmp_en))
                else:
                    F_zitu.append((Time[i[2]] - 1, tmp_en, Time[i[2]], up + 1))
                    Path.add((Time[i[2]] - 1, tmp_en, Time[i[2]], up + 1))
    return F_zitu

# 调用函数进行读取JSON文件
def last_element_sort(elem):
    return elem[-1]

x_data = []
y_data = []

def read_txt(in_file):
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
            if (entity.get(elements[1]) == None):
                entity[elements[1]] = en_num
                fan_entity[en_num]=elements[1]
                en_num += 1
            triple.append([entity[elements[0]], entity[elements[1]], elements[2][:7]])

    unique_tri =list(set(map(tuple, triple)))
    sorted_tri = sorted(unique_tri, key=last_element_sort)
    return sorted_tri

#sorted_T=read_json()
#event=read_txt_event("event0_time.txt")
sorted_T = read_txt(PATH + FILE)


event_id = entity[EVENT_NAME]
# sorted_zitu=get_zitu(event_id)
sorted_zitu = get_zitu_time(event_id)
F_zitu=filt_zitu(ENT_NUM) #控制子图中包含的实体数量 若输入大于1e7 则查看所有实体的路径
focus_entity = entity[FOCUS_ENT]

focus_entity_list = [entity[e] for e in FOCUS_ENT_LIST]

get_path()#获得子图路径

draw_lines_from_file(Path,"b")
#sorted_zitu=get_zitu(11208) #json


# 调用函数进行处理
#get_y_data("ys_node_92_20.txt")
#process_path_file("output_282.json")