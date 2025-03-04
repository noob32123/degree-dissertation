import csv

yes_count=0

# 第一类数据的分析
###################################################################
file_path = 'result_1.csv'

def convert_value(value_str):
    """ 将字符串转换为适当的数值类型 """
    try:

        return int(value_str)
    except ValueError:
        try:
   
            return float(value_str)
        except ValueError:

            return value_str


with open(file_path, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)


new_column_title = 'correct?'



for row in data_rows:
    if(min(row[15],row[16],row[17])==row[row[18]+15]):
        correct="yes"
        yes_count=yes_count+1
    else:
        correct="no"
    

    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title] = correct

    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path = 'correctness_evaluate_1.csv'

with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title])

    for row in data_rows:
        csv_writer.writerow(row)
    print("批量判断正确与否已经完成，正确率分析表格1已生成")
    print(f"1中有{yes_count}个yes")
    yes_count_1=yes_count



# 第二类数据的分析
###################################################################
file_path_2 = 'result_2.csv'

def convert_value(value_str):
    """ 将字符串转换为适当的数值类型 """
    try:

        return int(value_str)
    except ValueError:
        try:
   
            return float(value_str)
        except ValueError:

            return value_str


with open(file_path_2, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)


new_column_title = 'correct?'



for row in data_rows:
    if(min(row[15],row[16],row[17])==row[row[18]+15]):
        correct="yes"
        yes_count=yes_count+1
    else:
        correct="no"
    

    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title] = correct

    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title]]
    data_rows[data_rows.index(row)] = modified_row
    

yes_count_2=yes_count-yes_count_1
output_file_path_2 = 'correctness_evaluate_2.csv'

with open(output_file_path_2, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title])

    for row in data_rows:
        csv_writer.writerow(row)
    print("批量判断正确与否已经完成，正确率分析表格2已生成")

    print(f"2中有{yes_count_2}个yes")



# 第三类数据的分析
###################################################################
file_path_3 = 'result_3.csv'

def convert_value(value_str):
    """ 将字符串转换为适当的数值类型 """
    try:

        return int(value_str)
    except ValueError:
        try:
   
            return float(value_str)
        except ValueError:

            return value_str


with open(file_path_3, newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    
    header_row = next(csv_reader)

    data_rows = []

    for row in csv_reader:
        row = [convert_value(cell) for cell in row]
        data_rows.append(row)


new_column_title = 'correct?'



for row in data_rows:
    if(min(row[15],row[16],row[17])==row[row[18]+15]):
        correct="yes"
        yes_count=yes_count+1
    else:
        correct="no"
    

    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title] = correct

    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path_3 = 'correctness_evaluate_3.csv'
yes_count_3=yes_count-yes_count_1-yes_count_2

with open(output_file_path_3, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title])

    for row in data_rows:
        csv_writer.writerow(row)
    print("批量判断正确与否已经完成，正确率分析表格3已生成")
    print(f"3中有{yes_count_3}个yes")

print(f"共有{yes_count}个正确判断的用例")