# 该程序分析时间分段数据，按照两跳生成事件子图，并筛选包含事件节点的路绘制路径

import json
import matplotlib.pyplot as plt
from pylab import mpl
import datetime as dt
from datetime import timedelta
from dateutil import parser
from dateutil import rrule
# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]
N = 500000
Time = {} #时间映射成数字
ys_Time = {}#数字映射成时间

sorted_T=[]
entity = {}
fan_entity={} #反向 数字-》实体
zitu_path=[]#子图路径按路径输出
Path=set()#子图路径按边输出
edges = set() #总图的所有边
fig, ax = plt.subplots(dpi=150, figsize=(40, 40))
# 统计该子图下每个实体出现的数量
zitu_entity = {}
# 子图下某个实体映射成的数字
ys_en = {}
#子图下某时间存在的三元组
tri_time=[set() for _ in range(N)]
#判断某边已经被考虑过路径
y_list=[]
y_label=[]
value_time=set() #有效时间
cnt=0
spec_path=set()
event_path=set()
# PATH = "“台湾关系法”/"

PATH = "台湾岛内政治事件_100/反美猪公投/"
FILE = "change.txt"
EVENT_NAME = "反美猪公投"
ENT_NUM = 20
FOCUS_ENT = "蔡英文"

# FOCUS_ENT_LIST = ['特朗普', '德国媒体', '美国官员', '中国', '美国国会',
# '俄罗斯', '美国', '中国大陆', '蔡英文', '习近平', '网络强国建设', '金正恩',
# '中俄关系', '乌克兰', '唐纳德·特朗普']

FOCUS_ENT_LIST = ['美国', '中国' ]

def draw_lines_from_file(path,s_path,col):
    if focus_entity not in ys_en:
        print(f"以{r_size}天为关联时间下不存在 {FOCUS_ENT} 实体,请调整关联时间范围")
        return
    # 初始化空列表来存储坐标点
    points = []
    label_list=[]
    v_time=list(value_time)
    start_time = dt.datetime.strptime(ys_Time[v_time[0]], "%Y-%m-%d").date()
    end_time = dt.datetime.strptime(ys_Time[v_time[len(v_time)-1]], "%Y-%m-%d").date()
    Months = rrule.rrule(rrule.MONTHLY, dtstart=start_time, until=end_time).count()
    for i in range(0,Months+1,1):
        label_list.append((start_time+timedelta(days=30)*i).strftime("%Y-%m"))
    #label_list = ["2020", "2021", "2022", "2023"]
    plt.xticks(range(0, (len(label_list)-1)*30+5, 30), label_list)

    l=0
    r = rrule.rrule(rrule.DAILY, dtstart=start_time, until=end_time).count()
    plt.plot([l, r], [ys_en[event_id], ys_en[event_id]], c='orange', linestyle='--')
    plt.yticks(list(y_list), y_label)
    plt.title(EVENT_NAME + "_event_path"  + str(ys_en[event_id])+'_'+str(r_size))
    #plt.savefig(event_name + '_' + str(ys_en[event_id]) + '.png')
    # 读取文件并解析每行数据
    for item in path:
        # 将两个点作为一个元组添加到列表中
        date1 = (dt.datetime.strptime(ys_Time[item[0]], "%Y-%m-%d").date()-start_time).days
        date2 = (dt.datetime.strptime(ys_Time[item[2]], "%Y-%m-%d").date()-start_time).days
        points.append(((date1, item[1]), (date2, item[3])))
    for values in y_list:
        if(values==ys_en[event_id]):
            plt.plot([l, r], [values,values], c='red', linestyle='--')
        elif (values in [ys_en[e] for e in focus_entity_list if e in ys_en.keys()]):
            plt.plot([l, r], [values, values], c='black', linestyle='--')
        elif (values==ys_en[focus_entity]):
            plt.plot([l, r], [values,values], c='green', linestyle='--')
        else:
             plt.plot([l, r], [values, values], c='black', linestyle='--')
    # 遍历所有点对，绘制线条
    for point_pair in points:
        ax.plot([point_pair[0][0], point_pair[1][0]],
                [point_pair[0][1], point_pair[1][1]],col)
        # plt.draw()
        # plt.pause(0.01)
        plt.scatter(point_pair[0][0], point_pair[0][1], s=10, marker='o', c='red')
        plt.scatter(point_pair[1][0], point_pair[1][1], s=10, marker='o', c='red')

    #特殊画线的路径
    spec_points=[]
    for item in s_path:
        # 将两个点作为一个元组添加到列表中
        # if (zitu_entity[item[1]] >= 3 and zitu_entity[item[3]] >= 3):  # 路径中该结点出现次数小于3 就滤掉
        date1 = (dt.datetime.strptime(ys_Time[item[0]], "%Y-%m-%d").date() - start_time).days
        date2 = (dt.datetime.strptime(ys_Time[item[2]], "%Y-%m-%d").date() - start_time).days
        spec_points.append(((date1, item[1]), (date2, item[3])))
        #spec_points.append(((item[0], ys_en[item[1]]), (item[2], ys_en[item[3]])))
    for point_pair in spec_points:
        ax.plot([point_pair[0][0], point_pair[1][0]],
                [point_pair[0][1], point_pair[1][1]],"r")
    plt.savefig(PATH + EVENT_NAME + "_event_path_" + str(ys_en[event_id]) +'_'+str(r_size)+'.png')
    # plt.show()

judge_edge_front={}
judge_edge_back={}
def find_paths_back(current_time, current_edge, path,size):
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
        for t in tri_time[current_time+i]:
            if current_en==t[0]:
                next_edges.append((current_time,t[0],current_time+i,t[1]))

    if len(next_edges) > 0:
        for next_edge in next_edges:
            if judge_edge_back.get(next_edge) == None:  # 这条边没有考虑过路径
                find_paths_back(next_edge[2], next_edge, path,size)
                judge_edge_back[next_edge] = True;

    # 按照边的形式输出 画图
    for edge in path:
        Path.add(edge)

    cnt+=1

    path.pop()
def find_paths_front(current_time, current_edge, path,size):
    path.insert(0,current_edge) #向头部插入边
    global cnt
    current_en = current_edge[1]
    next_edges=[]
    now_time = ys_Time[current_time]
    date1 = dt.datetime.strptime(now_time, "%Y-%m-%d").date()  ##datetime.date(2018, 1, 6)
    # 如果存在日期相差小于要求 且头尾对应的边 就加入到next_edges[]内
    for i in range(1, size + 1, 1):
        if current_time-i  not in ys_Time:continue
        pre_time = ys_Time[current_time - i]
        date2 = dt.datetime.strptime(pre_time, "%Y-%m-%d").date()  ##datetime.date(2018, 1, 9)
        # 计算两个日期date的天数差
        Days = (date1 - date2).days
        if (Days > size): continue;  # 日期相差超过要求 就不考虑
        for t in tri_time[current_time -i]:
            if current_en == t[1]:
                next_edges.append((current_time- i, t[0], current_time, t[1]))

    if len(next_edges) > 0:
        for next_edge in next_edges:
            if judge_edge_front.get(next_edge)==None : #这条边没有考虑过路径
                find_paths_front(next_edge[0], next_edge, path,size)
                judge_edge_front[next_edge]=True;

    #按照边的形式输出 画图

    for edge in path:
        Path.add(edge)

    cnt+=1
    path.pop(0)
def find_paths(edges, current_edge, path):
    path.append(current_edge)

    current_x = current_edge[2]
    current_y = current_edge[3]

    next_edges = [edge for edge in edges if edge[0] == current_x and edge[1] == current_y]
    if len(next_edges) > 0:
        for next_edge in next_edges:
            find_paths(edges, next_edge, path)
    flag1=False

    for edge in path :
        if edge[1] ==focus_entity :
            flag1=True
    if flag1==True:
        for edge in path:
            spec_path.add(edge)
def get_path(size):
    for edge in edges:
        path = []
        if( not edge[1]): # event-> 1 作为头实体  那就对event向前找路径 对另一实体向后找路径
            t=Time[edge[2]]
            tmp=(t-1,event_id,t,edge[0])
            #path.append(tmp)
            find_paths_back(t,tmp,path,size) #时间 边 路径
            find_paths_front(t,tmp,path,size)
        else:
            t = Time[edge[2]]
            tmp = (t - 1, edge[0], t, event_id)
            #path.append(tmp)
            find_paths_back(t, tmp, path,size)
            find_paths_front(t, tmp, path,size)

    l_path = list(Path)
    for edge in l_path:
        s_path = []
        find_paths(l_path, edge, s_path)

        #find_paths(F_zitu, edge, path)

def get_zitu(id):

    time_num = 1
    #把出现的时间按顺序添加到Time里
    for res in sorted_T:
        if res[2] not in Time :
            time_num += 1
            ys_Time[time_num] = res[2]
            Time[res[2]] = time_num
        a = int(res[0])
        b = int(res[1])
        # 建边 时间 res[2] i->j  edge[i].add(另一实体j，i是否作为头实体，时间)
        # end_time=dt.datetime.strptime(res[2], "%Y-%m-%d").date()
        # start_time = (end_time + dt.timedelta(days=-1)).strftime('%Y-%m-%d')
        #将与事件有关的边填入edge内
        if(a==event_id):
            edges.add((b, 0, res[2]))  # 时间 res[2] a->b
        elif (b==event_id):
            edges.add((a, 1, res[2]))
        # zitu.append([start_time, a, res[2], b])
        tri_time[Time[res[2]]].add((a, b))
    #举例: second_time=(2018, 1, 6)
    second_time = dt.datetime.strptime(ys_Time[2] , "%Y-%m-%d").date()
    ys_Time[1]=(second_time+dt.timedelta(days=-1)).strftime('%Y-%m-%d')
    Time[ys_Time[1]] = 1


def filt_zitu(num):

    for item in Path:
        zitu_entity[item[1]] = zitu_entity.get(item[1], 0) + 1
        zitu_entity[item[3]] = zitu_entity.get(item[3], 0) + 1
        value_time.add(item[0])
        value_time.add(item[2])

    sorted_en = sorted(zitu_entity.items(), key=lambda x: x[1], reverse=True)

    # 取出现次数最多的num个元素构成的子图
    l = 0
    r = len(sorted_en)
    down = 0
    up = 1e5
    if num < 1e7:
        half_num =num// 2
        down = r // 2 - half_num
        up = r // 2 + half_num
    # 将出现最多的实体编号映射到中间
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
            if(l>=num):break
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

    #与事件有关的一条路径内的实体不在出现最多的num个实体映射里 把他们加进去
    if (event_id not in num_en):
        if up  in ys_en.values():
            up+=1
        ys_en[event_id]=up
        num_en.append(event_id)
    ext=1
    for i in edges:
        if (i[0] not in num_en):
            while (up + ext in y_list):
                ext += 1
            ys_en[i[0]] = up + ext
            num_en.append(i[0])
            ext += 1
    #print(ys_en[event_id],zitu_entity[event_id])
    ys_path=[]
    ys_spec_path=[]
    with open(PATH + 'ys_node_mapping.txt', 'w',encoding='utf-8') as output_file:
        for i in num_en:
            output_file.write(f"{fan_entity[i]}  映射为： {ys_en[i]} 出现次数：{zitu_entity[i]} \n")
            # if(ys_en[i]>=down and ys_en[i[0]]<=up):
            y_list.append(ys_en[i])
            y_label.append(fan_entity[i])



    for item in Path:
        if item[1] not in ys_en or item[3] not in ys_en: continue #路径中结点不再出现最多的num个实体内 就滤掉
        a=ys_en[item[1]]
        b=ys_en[item[3]]  #统计每个三元组的头尾实体映射id
        ys_path.append((item[0],a,item[2],b))


    for item in spec_path:
        if item[1] not in ys_en or item[3] not in ys_en: continue  # 路径中结点不再出现最多的num个实体内 就滤掉
        a=ys_en[item[1]]
        b=ys_en[item[3]]  #统计每个三元组的头尾实体映射id

        ys_spec_path.append((item[0],a,item[2],b))

    return ys_path,ys_spec_path

def last_element_sort(elem):
    return elem[-1]

x_data = []
y_data = []

def read_txt(in_file):
    triple=[]
    en_num=0
    with open(in_file,'r', encoding='utf-8') as file:
        for line in file:
            elements = line.strip().split()
            if(len(elements)>6) :continue
            if (entity.get(elements[0]) == None):
                entity[elements[0]] = en_num
                fan_entity[en_num] = elements[0]
                en_num += 1
            if (entity.get(elements[3]) == None):
                entity[elements[3]] = en_num
                fan_entity[en_num] = elements[3]
                en_num += 1
            triple.append([entity[elements[0]], entity[elements[3]], elements[5]])


    unique_tri =list(set(map(tuple, triple)))
    sorted_tri = sorted(unique_tri, key=last_element_sort)
    return sorted_tri

#sorted_T=read_json()
#event=read_txt_event("event0_time.txt")
sorted_T=read_txt(PATH + FILE)


event_id=entity[EVENT_NAME]
get_zitu(event_id)

focus_entity=entity[FOCUS_ENT]
focus_entity_list = [entity[e] for e in FOCUS_ENT_LIST]
r_size=15 #限制范围
get_path(r_size)#获得子图路径 限制范围
ys_path,ys_spec_path=filt_zitu(ENT_NUM) #控制子图中包含的实体数量 若输入大于1e7 则查看所有实体的路径
print(cnt)

draw_lines_from_file(ys_path,ys_spec_path,"b")
# sorted_zitu=get_zitu(11208) #json


# 调用函数进行处理
#get_y_data("ys_node_92_20.txt")
#process_path_file("output_282.json")