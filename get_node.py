# Function:读取csv文件，统计实体的频率，并将实体和频率输出到文件
import csv

def count_entities(csv_file):
    entity_freq = {}

    with open(csv_file,'r', encoding='utf-8') as file:
        for line in file:
            elements = line.strip().split(',')
            h_entity = elements[0]
            t_entity = elements[3]
            if h_entity in entity_freq:
                entity_freq[h_entity] += 1
            else:
                entity_freq[h_entity] = 1
            if t_entity in entity_freq:
                entity_freq[t_entity] += 1
            else:
                entity_freq[t_entity] = 1

    
    
    entity_set = set(entity_freq.keys())
    return entity_set, entity_freq

# Replace 'path/to/csv/file.csv' with the actual path to your CSV file
csv_file_path = '国际政治事件_frequency_10\反美猪公投\graph0.csv'
entities, frequencies = count_entities(csv_file_path)

# print("Entities:")
# for entity in entities:
#     print(entity)

# print("\nFrequencies:")

# 将实体和频率输出到文件
with open('国际政治事件_frequency_10\反美猪公投\entities.txt', 'w', encoding='utf-8') as f:
    f.write(f"Num_Entities: {len(entities)}\n")
    for entity, freq in frequencies.items():
        f.write(f"{entity}: {freq}\n")

# for entity, freq in frequencies.items():
#     print(entity, ":", freq)