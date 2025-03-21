import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import math
import time

start_time = time.time()
print(f"CUDA is available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")

device = torch.device("cuda:1")
 
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
        x = torch.relu(x) 
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
    
    def choose_action(self, state_tensor, epsilon):
        if random.random() < epsilon:
            return random.randint(0, 2)  # 随机探索
        else:
            # state_tensor = torch.FloatTensor(state).unsqueeze(0)
            
            with torch.no_grad():
                q_values = self.q_net(state_tensor)
            return q_values.argmax().item()
    
    def update(self, batch_size):
        if len(self.replay_buffer) < batch_size:
            return
        
        batch = random.sample(self.replay_buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
    
        # states = torch.FloatTensor(np.array(states))
        # next_states = torch.FloatTensor(np.array(next_states))
        states1 = torch.stack(states)
        states1 = states1.to(device)
        next_states = [torch.tensor(row) for row in next_states]
        next_states1 = torch.stack(next_states)
        next_states1 = next_states1.to(device)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        dones = torch.FloatTensor(dones)
        actions = actions.to(device)
        rewards = rewards.to(device)
        dones = dones.to(device)
        # 计算Q值
        # print(actions.unsqueeze(1).shape)
        # print(states1.shape)
        # print(next_states1.shape)
        # print(self.q_net(states1).shape)
        states1 = states1.squeeze(1)
        current_q = self.q_net(states1).gather(1, actions.unsqueeze(1))
        next_q = self.target_net(next_states1).max(1)[0].detach()

        #target_q = rewards + (1 - dones) * self.gamma * next_q
        target_q = rewards + self.gamma * next_q
        
        # 计算损失并更新
        loss = nn.MSELoss()(current_q.squeeze(), target_q)
        print(loss)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

# ====================== 4. 训练过程 ======================
env = StrategyOptimizationEnv()
agent = DQNAgent(env.state_dim, env.action_dim)

epsilon = 1.0
epsilon_decay = 0.9999
batch_size = 256


agent.q_net.to(device) 
agent.target_net.to(device) 

# print(agent.q_net.state_dict()['fc1.weight'])
# print(agent.target_net.state_dict()['fc1.weight'])

for episode in range(300000):
    state = env.reset()
    state_tensor = torch.FloatTensor(state).unsqueeze(0)
    state_tensor=state_tensor.to(device)
    action = agent.choose_action(state_tensor, epsilon)
    next_state, reward, done, _ = env.step(action)
    agent.replay_buffer.append((state_tensor, action, reward, next_state, done))
    
    # if(episode==140000):
    #     epsilon=1.0
    #     tag=1

    if len(agent.replay_buffer) >= batch_size:
        agent.update(batch_size) 
    
    epsilon = max(0.01, epsilon * epsilon_decay)
    
    
    print(f"Episode {episode}, Epsilon: {epsilon:.3f}")

    if (episode % 500 == 0):
        agent.target_net.load_state_dict(agent.q_net.state_dict())

    # torch.save(agent.q_net.state_dict(), f'model_saved_3.pth')
torch.save(agent.q_net.state_dict(), f'test_copy.pth')
print(agent.q_net.state_dict()['fc1.weight'])
print(agent.target_net.state_dict()['fc1.weight'])

end_time = time.time()
total_time = start_time-end_time
print(total_time)
# ====================== 5. 测试模型 ======================

agent.q_net.load_state_dict(torch.load(f'model_saved_7.pth'))
agent.target_net.load_state_dict(agent.q_net.state_dict())

state = env.reset()
state_tensor = torch.FloatTensor(state).unsqueeze(0)
state_tensor=state_tensor.to(device)
loss1 = (2*0.2*math.tan((math.pi/2)*(state[0]/5000)))+(0.002*0.2*state[1])+(0.002*((0.1*state[2])+(0.1*state[3])))+(0.02*0.2*state[4])+2*0.2*math.tan((math.pi/2)*(state[5]/5000)) # 策略A
loss2 = (2*(1/3)*math.tan((math.pi/2)*(state[6]/5000)))+(0.0015*(1/3)*state[7])+2*0.2*math.tan((math.pi/2)*(state[8]/5000))  # 策略B
loss3 = (2*0.2*math.tan((math.pi/2)*((state[9]+state[10])/5000)))+(0.002*((0.2*state[11])+(0.2*state[12])))+(0.002*0.2*state[13])+2*0.2*math.tan((math.pi/2)*(state[14]/5000))
action = agent.choose_action(state_tensor, epsilon=0)  # 关闭探索
print(loss1,loss2,loss3)
print(f"最优策略: {action}")
