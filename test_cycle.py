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
    
    def step(self, action):
        # 计算损失
        
        if action == 0:
            loss = (2*0.2*math.tan((math.pi/2)*(self.Q1/5000)))+(0.002*0.2*self.FLOPs1)+(0.002*((0.1*self.t1_PROCESS)+(0.1*self.t1_TRANSMIT)))+(0.02*0.2*self.fn)+2*0.2*math.tan((math.pi/2)*(self.B1/5000))    # 策略A
        elif action == 1:
            loss = (2*(1/3)*math.tan((math.pi/2)*(self.Q2/5000)))+(0.0015*(1/3)*self.t2_TRANSMIT)+2*0.2*math.tan((math.pi/2)*(self.B2/5000))  # 策略B
        elif action == 2:
            loss = (2*0.2*math.tan((math.pi/2)*((self.Q3_pre+self.Q3_trans)/5000)))+(0.002*0.2*self.FLOPs3)+(0.002*((0.2*self.t3_pre)+(0.2*self.t3_trans)))+2*0.2*math.tan((math.pi/2)*(self.B3/5000)) # 策略C
        
        # 奖励为负损失
        reward = -loss
        done = True  # 每次选择后任务结束
        return self.state, reward, done, {}

# ====================== 2. 定义神经网络 ======================
class QNetwork(nn.Module):
    # def __init__(self, state_dim, action_dim):
    #     super(QNetwork, self).__init__()
    #     self.fc1 = nn.Linear(state_dim, 64)
    #     self.fc2 = nn.Linear(64, 64)
    #     self.fc3 = nn.Linear(64, action_dim)
    
    # def forward(self, x):
    #     x = torch.relu(self.fc1(x))
    #     x = torch.relu(self.fc2(x))
    #     return self.fc3(x)
    def __init__(self, state_dim, action_dim):
        super(QNetwork, self).__init__()
        
        # 第一层：输入状态维度到128神经元，带BatchNorm和Dropout
        self.fc1 = nn.Linear(state_dim, 128)
        # self.bn1 = nn.BatchNorm1d(128)  # Batch Normalization层
        self.dropout1 = nn.Dropout(0.3)  # Dropout概率为0.3
        
        # 第二层：128神经元到256神经元，带BatchNorm和Dropout
        self.fc2 = nn.Linear(128, 256)
        # self.bn2 = nn.BatchNorm1d(256)
        self.dropout2 = nn.Dropout(0.3)
        
        # 第三层：256神经元到64神经元，带BatchNorm和Dropout
        self.fc3 = nn.Linear(256, 64)
        # self.bn3 = nn.BatchNorm1d(64)
        self.dropout3 = nn.Dropout(0.3)
        
        # 输出层：64神经元到动作维度
        self.fc4 = nn.Linear(64, action_dim)
    
    def forward(self, x):
        # 第一层前向传播
        x = self.fc1(x)
        x = torch.relu(x)  # 使用ELU激活函数
        # x = self.bn1(x)
        x = self.dropout1(x)
        
        # 第二层前向传播
        x = self.fc2(x)
        x = torch.relu(x)
        # x = self.bn2(x)
        x = self.dropout2(x)
        
        # 第三层前向传播
        x = self.fc3(x)
        x = torch.relu(x)
        # x = self.bn3(x)
        x = self.dropout3(x)
        
        # 输出层
        x = self.fc4(x)
        
        return x

# ====================== 3. 定义DQN智能体 ======================
class DQNAgent:
    def __init__(self, state_dim, action_dim, lr=1e-4, gamma=0.9):
        self.q_net = QNetwork(state_dim, action_dim)
        self.target_net = QNetwork(state_dim, action_dim)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)
        self.gamma = gamma
        self.replay_buffer = deque(maxlen=1000000)
    
    def choose_action(self, state, epsilon):
        if random.random() < epsilon:
            return random.randint(0, 2)  # 随机探索
        else:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                q_values = self.q_net(state_tensor)
            return q_values.argmax().item()
    
    def update(self, batch_size):
        if len(self.replay_buffer) < batch_size:
            return
        
        batch = random.sample(self.replay_buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        states = torch.FloatTensor(np.array(states))
        next_states = torch.FloatTensor(np.array(next_states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        dones = torch.FloatTensor(dones)
        
        # 计算Q值
        current_q = self.q_net(states).gather(1, actions.unsqueeze(1))
        next_q = self.target_net(next_states).max(1)[0].detach()
        target_q = rewards + (1 - dones) * self.gamma * next_q
        
        # 计算损失并更新
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        print(loss)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


env = StrategyOptimizationEnv()
agent = DQNAgent(env.state_dim, env.action_dim)

agent.q_net.load_state_dict(torch.load(f'model_saved_7.pth'))
agent.target_net.load_state_dict(agent.q_net.state_dict())

agent.q_net.eval()
agent.target_net.eval()


file_path = 'generated_data_section_3.csv'

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
    action = agent.choose_action(state, epsilon=0)  # 关闭探索
    # print(loss0,loss1,loss2)
    print(f"最优策略: {action}")


    current_row_dict = {header: value for header, value in zip(header_row, row)}

    current_row_dict[new_column_title3] = action
    current_row_dict[new_column_title0] = loss0
    current_row_dict[new_column_title1] = loss1
    current_row_dict[new_column_title2] = loss2
    

    modified_row = [current_row_dict[header] for header in header_row + [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3]]
    data_rows[data_rows.index(row)] = modified_row



output_file_path = 'result_3.csv'

with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:

    csv_writer = csv.writer(csvfile)

    csv_writer.writerow(header_row+ [new_column_title0]+ [new_column_title1]+ [new_column_title2]+ [new_column_title3])

    for row in data_rows:
        csv_writer.writerow(row)
    print("推理已经完成，result_x.csv表格已生成")

