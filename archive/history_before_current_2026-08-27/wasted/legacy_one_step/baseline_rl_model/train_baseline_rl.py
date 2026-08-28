import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import math

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




device = torch.device("cuda:0")

# 初始化模型和优化器
input_size = 15
output_size = 3
model = DecisionNetwork(input_size, output_size)
strat = StrategyOptimizationEnv()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)
model=model.to(device)

# 训练模型
epoch= 12000
batch_size = 32

for i in range(epoch):
    batch_data=[]
    truth_data=[]
    outputs=[]
    for j in range(0,batch_size):
        temp_input = strat.reset()
        batch_data.append(temp_input)
        truth_data.append(strat.calculate_truth())
        # temp_input=torch.tensor(temp_input)
        # temp_input=temp_input.to(device)
        # action = model(temp_input)
        # outputs.append(action)
     
    
    truth_data=torch.tensor(truth_data)  
    truth_data=truth_data.to(device)
    outputs=model(torch.tensor(batch_data).to(device))
    # print(outputs)
    # print(truth_data)
    loss = criterion(outputs, truth_data)
        
        
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    print(f'epoch [{i}], Loss: {loss.item():.4f}')

torch.save(model.state_dict(), f'test_model_12000.pth')

def choose_action(features):
    with torch.no_grad():
        # 将输入特征转换为Tensor（如果还不是的话）
        inputs = torch.tensor(features)
        # 前向传播，得到三个动作的消耗值
        outputs = model(inputs)
        # 选择消耗最少的动作索引
        _, predicted_indices = torch.min(outputs.data, dim=0)
        return predicted_indices.item()