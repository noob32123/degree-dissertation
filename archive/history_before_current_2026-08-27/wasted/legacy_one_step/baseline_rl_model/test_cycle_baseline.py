import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import math
import csv


print(f"CUDA is available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")

class StrategyOptimizationEnv:
    def __init__(self):
        self.state_dim = 15 
        self.action_dim = 3  # 3种策略
        
        self.reset()
    
    def reset(self):
        # 随机生成ACTION1常数参数
        self.Q1=np.random.uniform(0,1000)
        self.FLOPs1=np.random.uniform(0,1000)
        self.t1_PROCESS=np.random.uniform(0,1000)
        self.t1_TRANSMIT=np.random.uniform(200,300)
        self.fn=pow(np.random.randint(0,50),2)
        self.B1=np.random.uniform(0,1000)
        # ACTION2
        self.Q2=np.random.uniform(0,1000)
        self.t2_TRANSMIT=np.random.uniform(200,20000)
        self.B2=np.random.uniform(0,1000)
        # ACTION3
        self.temp3=np.random.uniform(0,1000)
        self.Q3_pre=np.random.uniform(0,self.temp3)
        self.Q3_trans=self.temp3-self.Q3_pre
        self.t3_pre=np.random.uniform(0,1000)
        self.t3_trans=np.random.uniform(200,20000)
        self.FLOPs3=np.random.uniform(0,1000)
        self.B3=np.random.uniform(0,1000)
        self.state=[self.Q1,self.FLOPs1,self.t1_PROCESS,self.t1_TRANSMIT,self.fn,self.B1,
                    self.Q2,self.t2_TRANSMIT,self.B2,
                    self.Q3_pre,self.Q3_trans,self.t3_pre,self.t3_trans,self.FLOPs3,self.B3]  
        return self.state
    
    def calculate_truth(self):
        # 计算损失
        
        
        loss1 = (2*0.2*math.tan((math.pi/2)*(self.Q1/5000)))+(0.002*0.2*self.FLOPs1)+(0.002*((0.1*self.t1_PROCESS)+(0.1*self.t1_TRANSMIT)))+(0.02*0.2*self.fn)+2*0.2*math.tan((math.pi/2)*(self.B1/5000))    # 策略A
        
        loss2 = (2*(1/3)*math.tan((math.pi/2)*(self.Q2/5000)))+(0.0015*(1/3)*self.t2_TRANSMIT)+2*0.2*math.tan((math.pi/2)*(self.B2/5000))  # 策略B
        
        loss3 = (2*0.2*math.tan((math.pi/2)*((self.Q3_pre+self.Q3_trans)/5000)))+(0.002*0.2*self.FLOPs3)+(0.002*((0.2*self.t3_pre)+(0.2*self.t3_trans)))+2*0.2*math.tan((math.pi/2)*(self.B3/5000)) # 策略C
        
        return(loss1,loss2,loss3)


       
    
# 定义神经网络模型
class DecisionNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(DecisionNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 32)
        self.fc3 = nn.Linear(32, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x


env = StrategyOptimizationEnv()
model=DecisionNetwork(15,3)

model.load_state_dict(torch.load(f'test_model_12000.pth'))#############model_set


model.eval()


def choose_action(features):
    with torch.no_grad():
        # 将输入特征转换为Tensor（如果还不是的话）
        inputs = torch.tensor(features)
        # 前向传播，得到三个动作的消耗值
        outputs = model(inputs)
        # 选择消耗最少的动作索引
        _, predicted_indices = torch.min(outputs.data, dim=0)
        return predicted_indices.item()


file_path = '../generated_data_section_1.csv'

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


new_column_title0 = 'loss0'
new_column_title1 = 'loss1'
new_column_title2 = 'loss2'
new_column_title3 = 'action'


for row in data_rows:

    state = row
    print(state)
     
    loss0 = (2*0.2*math.tan((math.pi/2)*(state[0]/5000)))+(0.002*0.2*state[1])+(0.002*((0.1*state[2])+(0.1*state[3])))+(0.02*0.2*state[4])+2*0.2*math.tan((math.pi/2)*(state[5]/5000)) # 策略A
    loss1 = (2*(1/3)*math.tan((math.pi/2)*(state[6]/5000)))+(0.0015*(1/3)*state[7])+2*0.2*math.tan((math.pi/2)*(state[8]/5000))  # 策略B
    loss2 = (2*0.2*math.tan((math.pi/2)*((state[9]+state[10])/5000)))+(0.002*((0.2*state[11])+(0.2*state[12])))+(0.002*0.2*state[13])+2*0.2*math.tan((math.pi/2)*(state[14]/5000))
    action = choose_action(state)  # 关闭探索
    # print(loss0,loss1,loss2)
    print(f"最优策略: {action}")


    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title3] = action
    current_row_dict[new_column_title0] = loss0
    current_row_dict[new_column_title1] = loss1
    current_row_dict[new_column_title2] = loss2
    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path = '../result_1.csv'

with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3])

    for row in data_rows:
        csv_writer.writerow(row)
    print("推理已经完成，result_1.csv表格已生成")

# chart2
file_path = '../generated_data_section_2.csv'

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


new_column_title0 = 'loss0'
new_column_title1 = 'loss1'
new_column_title2 = 'loss2'
new_column_title3 = 'action'


for row in data_rows:

    state = row
    print(state)
     
    loss0 = (2*0.2*math.tan((math.pi/2)*(state[0]/5000)))+(0.002*0.2*state[1])+(0.002*((0.1*state[2])+(0.1*state[3])))+(0.02*0.2*state[4])+2*0.2*math.tan((math.pi/2)*(state[5]/5000)) # 策略A
    loss1 = (2*(1/3)*math.tan((math.pi/2)*(state[6]/5000)))+(0.0015*(1/3)*state[7])+2*0.2*math.tan((math.pi/2)*(state[8]/5000))  # 策略B
    loss2 = (2*0.2*math.tan((math.pi/2)*((state[9]+state[10])/5000)))+(0.002*((0.2*state[11])+(0.2*state[12])))+(0.002*0.2*state[13])+2*0.2*math.tan((math.pi/2)*(state[14]/5000))
    action = choose_action(state)  # 关闭探索
    # print(loss0,loss1,loss2)
    print(f"最优策略: {action}")


    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title3] = action
    current_row_dict[new_column_title0] = loss0
    current_row_dict[new_column_title1] = loss1
    current_row_dict[new_column_title2] = loss2
    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path = '../result_2.csv'

with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3])

    for row in data_rows:
        csv_writer.writerow(row)
    print("推理已经完成，result_2.csv表格已生成")

# chart3
file_path = '../generated_data_section_3.csv'

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


new_column_title0 = 'loss0'
new_column_title1 = 'loss1'
new_column_title2 = 'loss2'
new_column_title3 = 'action'


for row in data_rows:

    state = row
    print(state)
     
    loss0 = (2*0.2*math.tan((math.pi/2)*(state[0]/5000)))+(0.002*0.2*state[1])+(0.002*((0.1*state[2])+(0.1*state[3])))+(0.02*0.2*state[4])+2*0.2*math.tan((math.pi/2)*(state[5]/5000)) # 策略A
    loss1 = (2*(1/3)*math.tan((math.pi/2)*(state[6]/5000)))+(0.0015*(1/3)*state[7])+2*0.2*math.tan((math.pi/2)*(state[8]/5000))  # 策略B
    loss2 = (2*0.2*math.tan((math.pi/2)*((state[9]+state[10])/5000)))+(0.002*((0.2*state[11])+(0.2*state[12])))+(0.002*0.2*state[13])+2*0.2*math.tan((math.pi/2)*(state[14]/5000))
    action = choose_action(state)  # 关闭探索
    # print(loss0,loss1,loss2)
    print(f"最优策略: {action}")


    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title3] = action
    current_row_dict[new_column_title0] = loss0
    current_row_dict[new_column_title1] = loss1
    current_row_dict[new_column_title2] = loss2
    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path = '../result_3.csv'

with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3])

    for row in data_rows:
        csv_writer.writerow(row)
    print("推理已经完成，result_3.csv表格已生成")









# # chart3
# file_path = '../generated_data_fullrange.csv'

# def convert_value(value_str):
#     """ 将字符串转换为适当的数值类型 """
#     try:

#         return int(value_str)
#     except ValueError:
#         try:
   
#             return float(value_str)
#         except ValueError:

#             return value_str


# with open(file_path, newline='', encoding='utf-8') as csvfile:
#     csv_reader = csv.reader(csvfile)
    
#     header_row = next(csv_reader)

#     data_rows = []

#     for row in csv_reader:
#         row = [convert_value(cell) for cell in row]
#         data_rows.append(row)


# new_column_title0 = 'loss0'
# new_column_title1 = 'loss1'
# new_column_title2 = 'loss2'
# new_column_title3 = 'action'


# for row in data_rows:

#     state = row
#     print(state)
     
#     loss0 = (2*0.2*math.tan((math.pi/2)*(state[0]/5000)))+(0.002*0.2*state[1])+(0.002*((0.1*state[2])+(0.1*state[3])))+(0.02*0.2*state[4])+2*0.2*math.tan((math.pi/2)*(state[5]/5000)) # 策略A
#     loss1 = (2*(1/3)*math.tan((math.pi/2)*(state[6]/5000)))+(0.0015*(1/3)*state[7])+2*0.2*math.tan((math.pi/2)*(state[8]/5000))  # 策略B
#     loss2 = (2*0.2*math.tan((math.pi/2)*((state[9]+state[10])/5000)))+(0.002*((0.2*state[11])+(0.2*state[12])))+(0.002*0.2*state[13])+2*0.2*math.tan((math.pi/2)*(state[14]/5000))
#     action = choose_action(state)  # 关闭探索
#     # print(loss0,loss1,loss2)
#     print(f"最优策略: {action}")


#     current_row_dict = {header: value for header, value in zip(header_row, row)}

#     current_row_dict[new_column_title3] = action
#     current_row_dict[new_column_title0] = loss0
#     current_row_dict[new_column_title1] = loss1
#     current_row_dict[new_column_title2] = loss2
    

#     modified_row = [current_row_dict[header] for header in header_row + [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3]]
#     data_rows[data_rows.index(row)] = modified_row



# output_file_path = '../result_fullrange.csv'

# with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

#     csv_writer = csv.writer(csvfile)

#     csv_writer.writerow(header_row+ [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3])

#     for row in data_rows:
#         csv_writer.writerow(row)
#     print("推理已经完成，result_fullrange.csv表格已生成")