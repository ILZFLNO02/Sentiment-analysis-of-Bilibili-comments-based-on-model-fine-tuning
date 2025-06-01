import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import torch

# 全局只加载一次模型和分词器
MODEL_PATH = "e:/bilibili_train/bert_train"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(DEVICE)
model.eval()

def predict_sentiment(texts, batch_size=64):
    results = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            encodings = tokenizer(batch_texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
            input_ids = encodings["input_ids"].to(DEVICE)
            attention_mask = encodings["attention_mask"].to(DEVICE)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1).cpu().numpy()
            results.extend(preds)
    return results

def analyze_sentiment(filepath, save_file, model_path=None):
    # model_path参数保留兼容性，但实际用全局加载的模型
    data = pd.read_excel(filepath, names=["名字", "性别", "等级", "评论内容", "点赞数"], usecols=[0, 1, 2, 3, 4])
    comments = data['评论内容'].astype(str).tolist()

    preds = predict_sentiment(comments)
    id2label = {0: "负向", 1: "正向", 2: "中向"}
    data['BERT标签'] = [id2label[x] for x in preds]

    data.to_excel(save_file, index=False)
    return save_file

if __name__ == "__main__":
    analyze_sentiment(
        "评论信息.xlsx",
        "情感输出结果_bert.xlsx",
        "e:/bilibili_train/bert_train"
    )