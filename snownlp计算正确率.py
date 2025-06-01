import pandas as pd
from snownlp import SnowNLP
from sklearn.metrics import accuracy_score, f1_score

# 读取数据
df = pd.read_excel(r'e:\bilibili_train\评论情感分析结果_三分类_人工纠错.xlsx')

# 标签映射（首字母大写）
label_map = {"Negative": 0, "Neutral": 1, "Positive": 2}

# 只保留有效标签的行
df = df[df['emotion'].isin(label_map.keys())]

labels = [label_map[x] for x in df['emotion']]
comments = df['comment'].astype(str).tolist()

# SnowNLP预测
def snownlp_predict(text):
    s = SnowNLP(text)
    score = s.sentiments
    # 三分类阈值划分
    if score > 0.6:
        return 2  # Positive
    elif score < 0.4:
        return 0  # Negative
    else:
        return 1  # Neutral

preds = [snownlp_predict(c) for c in comments]

# 计算准确率和F1值
acc = accuracy_score(labels, preds)
f1 = f1_score(labels, preds, average='macro')

print(f"SnowNLP三分类准确率: {acc:.4f}")
print(f"SnowNLP三分类F1值: {f1:.4f}")