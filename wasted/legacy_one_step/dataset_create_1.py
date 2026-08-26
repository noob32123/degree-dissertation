import pandas as pd
import numpy as np
import random



num_records = 5000

data = []

for _ in range(num_records):
    
    # 随机生成ACTION1常数参数
    Q1=np.random.uniform(200,300)
    FLOPs1=np.random.uniform(100,400)
    t1_PROCESS=np.random.uniform(100,400)
    t1_TRANSMIT=np.random.uniform(200,300)
    fn=pow(np.random.randint(0,3),2)
    B1=np.random.uniform(20,100)
    # ACTION2
    Q2=np.random.uniform(600,1000)
    t2_TRANSMIT=np.random.uniform(15000,20000)
    B2=np.random.uniform(900,1000)
    # ACTION3
    temp3=np.random.uniform(900,1000)
    Q3_pre=np.random.uniform(0,temp3)
    Q3_trans=temp3-Q3_pre
    t3_pre=np.random.uniform(700,1000)
    t3_trans=np.random.uniform(10000,15000)
    FLOPs3=np.random.uniform(100,900)
    B3=np.random.uniform(600,800)
    data.append({
        'Q1': Q1,
        'FLOPs1': FLOPs1,
        't1_PROCESS': t1_PROCESS,
        't1_TRANSMIT': t1_TRANSMIT,
        'fn': fn, 
        'B1': B1,
        'Q2': Q2,
        't2_TRANSMIT': t2_TRANSMIT,
        'B2': B2,
        'Q3_pre': Q3_pre,
        'Q3_trans': Q3_trans,  
        't3_pre': t3_pre,
        't3_trans': t3_trans,  
        'FLOPs3': FLOPs3,
        'B3': B3
    })

# 创建DataFrame
df = pd.DataFrame(data)



# 保存到CSV文件
output_path_csv = 'generated_data_section_1.csv'
df.to_csv(output_path_csv, index=False)
print(f"数据已保存到 {output_path_csv}")


