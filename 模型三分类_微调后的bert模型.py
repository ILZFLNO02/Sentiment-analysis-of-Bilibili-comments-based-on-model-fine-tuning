# 导入必要的库 (保持不变)
import pandas as pd
import os
import datasets
import torch
from transformers import BertTokenizer, BertForSequenceClassification

# --- 配置部分 --- (保持不变)
# Excel文件路径
excel_file_path = 'e:\\bilibili_train\\多视频评论信息.xls'
# 包含评论内容的列名
comment_column_name = '评论内容'
# 输出文件名
output_file_name = '评论情感分析结果_三分类_本地模型批量预测.xlsx' # 修改输出文件名
# 你本地保存微调模型的目录路径
local_model_path = './bert_train'

# --- 加载本地微调模型和 Tokenizer --- (增加 FP16 转换)
try:
    print(f"尝试从本地目录 '{local_model_path}' 加载模型和 Tokenizer...")
    tokenizer = BertTokenizer.from_pretrained(local_model_path)
    print("Tokenizer 加载成功。")

    model = BertForSequenceClassification.from_pretrained(local_model_path)
    print("模型加载成功。")

    id2label_map = model.config.id2label
    print(f"获取标签映射: {id2label_map}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # 在有限显存环境下，启用 FP16 通常是必要的
    if device.type == 'cuda':
        try:
            model.half() # 将模型转换为半精度
            print("模型已转换为半精度 (FP16)。")
        except Exception as e:
            print(f"警告: 无法将模型转换为 FP16: {e}。将使用 FP32 进行预测，可能需要更小的 Batch Size。")

    print(f"模型已加载到设备: {device}")

except Exception as e:
    print(f"加载本地模型或 Tokenizer 失败: {e}")
    print(f"请检查目录 '{local_model_path}' 是否存在且包含正确的模型文件 (config.json, model.safetensors, vocab.txt 等)。")
    exit()

# --- 读取数据并进行情感分析 (手动批量处理方法) ---
# 修改函数，实现手动批量预测
def analyze_sentiments_from_excel_batch(file_path, column_name, tokenizer, model, id2label_map):
    """
    从Excel文件读取评论，进行预处理，使用加载的本地模型进行手动批量情感分析，并返回包含结果的列表。
    """
    try:
        df = pd.read_excel(file_path, engine='xlrd')
        print(f"成功读取Excel文件 '{file_path}'，共 {len(df)} 条数据。")
    except FileNotFoundError:
        print(f"错误：文件未找到 '{file_path}'")
        return None
    except Exception as e:
         print(f"读取Excel文件失败: {e}")
         return None

    if column_name not in df.columns:
        print(f"错误：列 '{column_name}' 在文件中未找到。可用的列: {df.columns.tolist()}")
        return None

    # 获取非空评论的原始索引列表和文本列表
    non_empty_original_indices = []
    non_empty_comments = []
    for original_idx, text in enumerate(df[column_name]):
        comment_text = str(text).strip()
        if comment_text:
            non_empty_original_indices.append(original_idx)
            non_empty_comments.append(comment_text)

    print(f"发现 {len(non_empty_comments)} 条非空评论，将进行预测。")

    # --- 手动批量预测的关键部分 ---
    # 为 4GB 显存环境设置预测的 Batch Size 和 Max Length
    # 你可能需要根据实际情况和是否成功启用 FP16 来微调 predict_batch_size
    predict_batch_size = 16 # 尝试一个较小的 Batch Size，例如 16 或 8
    predict_max_length = 128 # 在 4GB 环境下，将最大长度限制在 128 更安全

    print(f"将使用 手动批量预测，Batch Size = {predict_batch_size}, Max Length = {predict_max_length}。")

    all_predicted_labels = [] # 存储所有非空评论的预测文本标签
    all_predicted_scores = [] # 存储所有非空评论的预测最高得分

    # 将模型设置为评估模式 (在推理前设置)
    model.eval()

    # 使用 torch.no_grad() 禁用梯度计算 (在推理前设置)
    with torch.no_grad():
        # 手动循环处理批次
        for i in range(0, len(non_empty_comments), predict_batch_size):
            batch_start = i
            batch_end = i + predict_batch_size
            batch_texts = non_empty_comments[batch_start : batch_end]

            # 如果批量为空，跳过 (通常不会，除非总数不是 Batch Size 的倍数)
            if not batch_texts:
                continue

            try:
                # Tokenizer 编码当前批次文本
                inputs = tokenizer(
                    batch_texts,
                    padding=True,           # 在批次内进行填充
                    truncation=True,        # 截断到 predict_max_length
                    max_length=predict_max_length, # 使用为预测设定的最大长度
                    return_tensors="pt"     # 返回 PyTorch 张量
                )

                # 将输入张量移动到设备 (GPU)
                inputs = {key: val.to(model.device) for key, val in inputs.items()}

                # --- 修改：只将浮点类型的输入张量转换为半精度 ---
                if model.dtype == torch.float16:
                     # 遍历 inputs 字典，如果张量是浮点类型，则转换为 half()
                     inputs = {
                         key: val.half() if val.dtype in [torch.float32, torch.float] else val
                         for key, val in inputs.items()
                     }
                # --- 修改结束 ---

                # 将编码后的输入送入模型进行推理
                outputs = model(**inputs)

                # 获取当前批次的预测结果
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                max_probs, predicted_ids = torch.max(probabilities, dim=-1)

                # 将结果从张量转换为 Python 列表
                batch_predicted_ids = predicted_ids.cpu().tolist()
                batch_max_probs = max_probs.cpu().tolist()

                # 将类别 ID 转换为文本标签和得分
                batch_predicted_labels = [id2label_map[id] for id in batch_predicted_ids]
                batch_predicted_scores = batch_max_probs

                # 将当前批次的预测结果添加到总的结果列表
                all_predicted_labels.extend(batch_predicted_labels)
                all_predicted_scores.extend(batch_predicted_scores)

                print(f"已处理批次 {i // predict_batch_size + 1}/{(len(non_empty_comments) + predict_batch_size - 1) // predict_batch_size} (样本 {batch_start+1}-{batch_end})")


            except Exception as e:
                print(f"警告: 处理批次 (样本 {batch_start+1}-{batch_end}) 时发生错误: {e}")
                # 如果某个批次处理失败，这里简单打印警告并跳过该批次。
                # 这会导致最终结果中这些评论标记为“未分析”或“预测失败”。
                # 如果需要更严格的错误处理，可以根据错误类型选择退出或采取其他措施。
                pass

    # 检查是否有任何预测结果生成
    if not all_predicted_labels:
         print("所有批次处理失败或没有非空评论被成功预测。")
         return None # 如果没有成功预测任何评论，则表示整个分析失败

    print("本地模型预测流程完成。")

    # --- 整理结果，将分析结果与原始数据合并 ---
    # 预填充结果列表，包含原始数据和默认的分析状态
    results_list = []
    for i, row in df.iterrows():
         row_result = {
            'name': row.get('名字'),
            'gender': row.get('性别'),
            'level': row.get('等级'),
            column_name: str(row.get(column_name, '')),
            'likes': row.get('点赞数'),
            'emotion': '未分析', # 默认状态：未分析
            'score': None,
            'status': '未分析'  # 默认状态：未分析
        }
         results_list.append(row_result)

    # 将预测结果映射回原始位置
    # all_predicted_labels 和 all_predicted_scores 的长度与 non_empty_original_indices 相同
    # all_predicted_labels[i] 对应于原始 DataFrame 索引 non_empty_original_indices[i]
    if all_predicted_labels: # 确保有预测结果需要映射
        for i in range(len(all_predicted_labels)):
            original_idx = non_empty_original_indices[i] # 获取预测结果对应的原始索引

            results_list[original_idx]['emotion'] = all_predicted_labels[i]
            results_list[original_idx]['score'] = all_predicted_scores[i]
            results_list[original_idx]['status'] = '成功'

    # 最终遍历 results_list，处理空评论和标记预测失败的评论
    for i, row_result in enumerate(results_list):
        original_comment_text = str(df.iloc[i].get(column_name, '')).strip()
        if not original_comment_text and row_result['status'] == '未分析':
            # 如果是空评论且状态还是“未分析”，则标记为“跳过”
            row_result['emotion'] = '空评论'
            row_result['status'] = '跳过'
        elif row_result['status'] == '未分析':
             # 如果是非空评论，但在预测结果映射阶段状态仍然是“未分析”
             # 这意味着它在手动批量预测过程中失败了
             row_result['status'] = '预测失败 (批次错误)'
             row_result['emotion'] = '预测失败' # 或者保持 '未分析'

    return results_list

# --- 主程序执行部分 --- (保持不变)
# ... (你的主程序调用部分，与上次修改相同)
if __name__ == "__main__":
    # 调用函数进行分析，传递加载好的 tokenizer, model 和 id2label
    analysis_results = analyze_sentiments_from_excel_batch(
        excel_file_path,
        comment_column_name,
        tokenizer,
        model,
        id2label_map
    )

    if analysis_results is not None:
        output_df = pd.DataFrame(analysis_results)
        try:
            output_df.to_excel(output_file_name, index=False, engine='openpyxl')
            print(f"详细分析结果已保存到 '{output_file_name}'")
        except Exception as e:
            print(f"保存文件失败: {e}")
            print("请确保文件未被占用或检查写入权限。")

    print("\n脚本执行完毕。")