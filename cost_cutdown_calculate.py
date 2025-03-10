import csv

def convert_value(value_str):
    """ 将字符串转换为适当的数值类型 """
    try:

        return int(value_str)
    except ValueError:
        try:
   
            return float(value_str)
        except ValueError:

            return value_str

# chart1
file_path = 'result_1.csv'


with open(file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)



new_column_title1 = 'Q_rl'
new_column_title2 = 't_rl'
new_column_title3 = 'B_rl'
new_column_title4 = 'FLOPs_rl'



for row in data_rows:
    if(row[18]==0):
        Q_rl=row[0]
        t_rl=row[2]+row[3]
        B_rl=row[5]
        FLOPs_rl=row[1]
    elif(row[18]==1):
        Q_rl=row[6]
        t_rl=row[7]
        B_rl=row[8]
        FLOPs_rl=0
    elif(row[18]==2):
        Q_rl=row[9]+row[10]
        t_rl=row[11]+row[12]
        B_rl=row[14]
        FLOPs_rl=row[13]
    

    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title1] = Q_rl
    current_row_dict[new_column_title2] = t_rl
    current_row_dict[new_column_title3] = B_rl
    current_row_dict[new_column_title4] = FLOPs_rl

    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title1]+ [new_column_title2]+ [new_column_title3]+ [new_column_title4]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path = 'cost_cutdown_calculate1.csv'

with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title1]+ [new_column_title2]+ [new_column_title3]+ [new_column_title4])

    for row in data_rows:
        csv_writer.writerow(row)
    print("批量计算cost已经完成，表格1已生成")


# chart2
file_path = 'result_2.csv'


with open(file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)



new_column_title1 = 'Q_rl'
new_column_title2 = 't_rl'
new_column_title3 = 'B_rl'
new_column_title4 = 'FLOPs_rl'



for row in data_rows:
    if(row[18]==0):
        Q_rl=row[0]
        t_rl=row[2]+row[3]
        B_rl=row[5]
        FLOPs_rl=row[1]
    elif(row[18]==1):
        Q_rl=row[6]
        t_rl=row[7]
        B_rl=row[8]
        FLOPs_rl=0
    elif(row[18]==2):
        Q_rl=row[9]+row[10]
        t_rl=row[11]+row[12]
        B_rl=row[14]
        FLOPs_rl=row[13]
    

    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title1] = Q_rl
    current_row_dict[new_column_title2] = t_rl
    current_row_dict[new_column_title3] = B_rl
    current_row_dict[new_column_title4] = FLOPs_rl

    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title1]+ [new_column_title2]+ [new_column_title3]+ [new_column_title4]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path = 'cost_cutdown_calculate2.csv'

with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title1]+ [new_column_title2]+ [new_column_title3]+ [new_column_title4])

    for row in data_rows:
        csv_writer.writerow(row)
    print("批量计算cost已经完成，表格2已生成")

# chart3
file_path = 'result_3.csv'


with open(file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)



new_column_title1 = 'Q_rl'
new_column_title2 = 't_rl'
new_column_title3 = 'B_rl'
new_column_title4 = 'FLOPs_rl'



for row in data_rows:
    if(row[18]==0):
        Q_rl=row[0]
        t_rl=row[2]+row[3]
        B_rl=row[5]
        FLOPs_rl=row[1]
    elif(row[18]==1):
        Q_rl=row[6]
        t_rl=row[7]
        B_rl=row[8]
        FLOPs_rl=0
    elif(row[18]==2):
        Q_rl=row[9]+row[10]
        t_rl=row[11]+row[12]
        B_rl=row[14]
        FLOPs_rl=row[13]
    

    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title1] = Q_rl
    current_row_dict[new_column_title2] = t_rl
    current_row_dict[new_column_title3] = B_rl
    current_row_dict[new_column_title4] = FLOPs_rl

    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title1]+ [new_column_title2]+ [new_column_title3]+ [new_column_title4]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path = 'cost_cutdown_calculate3.csv'

with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title1]+ [new_column_title2]+ [new_column_title3]+ [new_column_title4])

    for row in data_rows:
        csv_writer.writerow(row)
    print("批量计算cost已经完成，表格3已生成")

# 统计部份函数
file_path = 'cost_cutdown_calculate1.csv'

with open(file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)

Q_rl_1=0
Q_1_1=0
Q_2_1=0
Q_3_1=0
t_rl_1=0
t_1_1=0
t_2_1=0
t_3_1=0
B_rl_1=0
B_1_1=0
B_2_1=0
B_3_1=0
FLOPs_rl_1=0
FLOPs_1_1=0
FLOPs_2_1=0
FLOPs_3_1=0

for row in data_rows:
    Q_rl_1=Q_rl_1+row[19]
    Q_1_1=Q_1_1+row[0]
    Q_2_1=Q_2_1+row[6]
    Q_3_1=Q_3_1+row[9]+row[10]

    t_rl_1=t_rl_1+row[20]
    t_1_1=t_1_1+row[2]+row[3]
    t_2_1=t_2_1+row[7]
    t_3_1=t_3_1+row[11]+row[12]

    B_rl_1=B_rl_1+row[21]
    B_1_1=B_1_1+row[5]
    B_2_1=B_2_1+row[8]
    B_3_1=B_3_1+row[14]

    FLOPs_rl_1=FLOPs_rl_1+row[22]
    FLOPs_1_1=FLOPs_1_1+row[1]
    FLOPs_2_1=FLOPs_2_1+0
    FLOPs_3_1=FLOPs_3_1+row[13]

print(f"表1中Q_rl总和为{Q_rl_1},Q_1总和为{Q_1_1},Q_2总和为{Q_2_1},Q_3总和为{Q_3_1},t_rl总和为{t_rl_1},t_1总和为{t_1_1},t_2总和为{t_2_1},t_3总和为{t_3_1},")
print(f"表1中B_rl总和为{B_rl_1},B_1总和为{B_1_1},B_2总和为{B_2_1},B_3总和为{B_3_1},FLOPs_rl总和为{FLOPs_rl_1},FLOPs_1总和为{FLOPs_1_1},FLOPs_2总和为{FLOPs_2_1},FLOPs_3总和为{FLOPs_3_1},")

# chart2
file_path = 'cost_cutdown_calculate2.csv'

with open(file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)

Q_rl_2=0
Q_1_2=0
Q_2_2=0
Q_3_2=0
t_rl_2=0
t_1_2=0
t_2_2=0
t_3_2=0
B_rl_2=0
B_1_2=0
B_2_2=0
B_3_2=0
FLOPs_rl_2=0
FLOPs_1_2=0
FLOPs_2_2=0
FLOPs_3_2=0

for row in data_rows:
    Q_rl_2=Q_rl_2+row[19]
    Q_1_2=Q_1_2+row[0]
    Q_2_2=Q_2_2+row[6]
    Q_3_2=Q_3_2+row[9]+row[10]

    t_rl_2=t_rl_2+row[20]
    t_1_2=t_1_2+row[2]+row[3]
    t_2_2=t_2_2+row[7]
    t_3_2=t_3_2+row[11]+row[12]

    B_rl_2=B_rl_2+row[21]
    B_1_2=B_1_2+row[5]
    B_2_2=B_2_2+row[8]
    B_3_2=B_3_2+row[14]

    FLOPs_rl_2=FLOPs_rl_2+row[22]
    FLOPs_1_2=FLOPs_1_2+row[1]
    FLOPs_2_2=FLOPs_2_2+0
    FLOPs_3_2=FLOPs_3_2+row[13]

print(f"表2中Q_rl总和为{Q_rl_2},Q_1总和为{Q_1_2},Q_2总和为{Q_2_2},Q_3总和为{Q_3_2},t_rl总和为{t_rl_2},t_1总和为{t_1_2},t_2总和为{t_2_2},t_3总和为{t_3_2},")
print(f"表2中B_rl总和为{B_rl_2},B_1总和为{B_1_2},B_2总和为{B_2_2},B_3总和为{B_3_2},FLOPs_rl总和为{FLOPs_rl_2},FLOPs_1总和为{FLOPs_1_2},FLOPs_2总和为{FLOPs_2_2},FLOPs_3总和为{FLOPs_3_2},")


# chart3
file_path = 'cost_cutdown_calculate3.csv'

with open(file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)

Q_rl_3=0
Q_1_3=0
Q_2_3=0
Q_3_3=0
t_rl_3=0
t_1_3=0
t_2_3=0
t_3_3=0
B_rl_3=0
B_1_3=0
B_2_3=0
B_3_3=0
FLOPs_rl_3=0
FLOPs_1_3=0
FLOPs_2_3=0
FLOPs_3_3=0

for row in data_rows:
    Q_rl_3=Q_rl_3+row[19]
    Q_1_3=Q_1_3+row[0]
    Q_2_3=Q_2_3+row[6]
    Q_3_3=Q_3_3+row[9]+row[10]

    t_rl_3=t_rl_3+row[20]
    t_1_3=t_1_3+row[2]+row[3]
    t_2_3=t_2_3+row[7]
    t_3_3=t_3_3+row[11]+row[12]

    B_rl_3=B_rl_3+row[21]
    B_1_3=B_1_3+row[5]
    B_2_3=B_2_3+row[8]
    B_3_3=B_3_3+row[14]

    FLOPs_rl_3=FLOPs_rl_3+row[22]
    FLOPs_1_3=FLOPs_1_3+row[1]
    FLOPs_2_3=FLOPs_2_3+0
    FLOPs_3_3=FLOPs_3_3+row[13]

print(f"表3中Q_rl总和为{Q_rl_3},Q_1总和为{Q_1_3},Q_2总和为{Q_2_3},Q_3总和为{Q_3_3},t_rl总和为{t_rl_3},t_1总和为{t_1_3},t_2总和为{t_2_3},t_3总和为{t_3_3},")
print(f"表3中B_rl总和为{B_rl_3},B_1总和为{B_1_3},B_2总和为{B_2_3},B_3总和为{B_3_3},FLOPs_rl总和为{FLOPs_rl_3},FLOPs_1总和为{FLOPs_1_3},FLOPs_2总和为{FLOPs_2_3},FLOPs_3总和为{FLOPs_3_3},")


print(f"总的Q_rl为{Q_rl_1+Q_rl_2+Q_rl_3},总的Q_1为{Q_1_1+Q_1_2+Q_1_3},总的Q_2为{Q_2_1+Q_2_2+Q_2_3},总的Q_3为{Q_3_1+Q_3_2+Q_3_3}.")
print(f"总的t_rl为{t_rl_1+t_rl_2+t_rl_3},总的t_1为{t_1_1+t_1_2+t_1_3},总的t_2为{t_2_1+t_2_2+t_2_3},总的t_3为{t_3_1+t_3_2+t_3_3}.")
print(f"总的B_rl为{B_rl_1+B_rl_2+B_rl_3},总的B_1为{B_1_1+B_1_2+B_1_3},总的B_2为{B_2_1+B_2_2+B_2_3},总的B_3为{B_3_1+B_3_2+B_3_3}.")
print(f"总的FLOPs_rl为{FLOPs_rl_1+FLOPs_rl_2+FLOPs_rl_3},总的FLOPs_1为{FLOPs_1_1+FLOPs_1_2+FLOPs_1_3},总的FLOPs_2为{FLOPs_2_1+FLOPs_2_2+FLOPs_2_3},总的FLOPs_3为{FLOPs_3_1+FLOPs_3_2+FLOPs_3_3}.")
