import csv
import os

fan_entity={} #反向 数字-》实体
PATH = f"消岐国际政治事件_4month/"
SAVE_PATH = PATH+"entity_related_to_TW/"
RANGE=100 # 提取出现次数最多的range个实体
def read_csv():
    '''
    读取文件
    '''
    #创建保存路径文件夹
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    for file_name in os.listdir(PATH):
        if file_name.endswith('.csv'):
            # 构建CSV文件的完整路径
            file_path = os.path.join(PATH, file_name)
            entity = {}
            # 打开CSV文件
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for elements in reader:
                    # elements = line.strip().split(",")
                    if (len(elements) > 6): continue
                    entity[elements[0]] = entity.get(elements[0],0)+1
                    entity[elements[3]] = entity.get(elements[3],0)+1

            sorted_en = sorted(entity.items(), key=lambda x: x[1], reverse=True)
            #输出txt 文件
            # 使用 "_" 分割文件名
            parts = file_name.split("_")
            # 获取第一个部分
            Output = parts[0]
            en_num=len(sorted_en)
            R=RANGE
            with open(SAVE_PATH + Output+'_en_related_TW.txt', 'w', encoding='utf-8') as output_file:
                #当前文件内的实体个数少于Range
                if(en_num<R):
                    print(f"{file_name} 文件内包含的实体数量少于{R},因此将所有实体全部输出")
                    R=en_num

                for i in range (0,R):
                    output_file.write(f"{sorted_en[i][0]} 出现次数： {sorted_en[i][1]}  \n")




if __name__ == '__main__':

    #sorted_T = read_txt(PATH + FILE)
    sorted_T = read_csv()