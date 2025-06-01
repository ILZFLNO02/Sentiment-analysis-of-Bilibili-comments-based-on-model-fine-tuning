from transformers import pipeline # 导入transformers库用于加载AI模型
import pandas as pd # 导入pandas库用于处理Excel文件
import os # 导入os库
import datasets # 导入datasets库用于批量处理数据

# --- 配置部分 ---
# Excel文件路径
excel_file_path = 'e:\\bilibili_train\\多视频评论信息.xls'
# 包含评论内容的列名
comment_column_name = '评论内容'
# 输出文件名
output_file_name = '评论情感分析结果_三分类.xlsx'

# --- 加载情感分析模型 ---
try:
    # 加载指定的中文情感分析模型
    # 使用 top_k=None 来获取所有类别的得分
    sentiment_pipeline = pipeline(
        "text-classification",
        model="IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment",
        top_k=None # 使用 top_k=None 获取所有得分
    )
    print("情感分析模型加载成功。")
except Exception as e:
    print(f"加载情感分析模型失败: {e}")
    print("请检查模型名称、网络或依赖。")
    exit() # 加载失败则退出脚本

# --- 读取数据并进行情感分析 (批量处理方法) ---
# 修改函数签名，接收 tokenizer, model 和 id2label 映射
def analyze_sentiments_from_excel_batch(file_path, column_name, tokenizer, model, id2label_map):
    """
    从Excel文件读取评论，进行预处理，使用加载的本地模型进行情感分析，并返回包含结果的列表。
    """
    try:
        # 读取Excel文件 (.xls 需要安装 xlrd)
        df = pd.read_excel(file_path, engine='xlrd')
        print(f"成功读取Excel文件 '{file_path}'，共 {len(df)} 条数据。")
    except FileNotFoundError:
        print(f"错误：文件未找到 '{file_path}'")
        return None
    except Exception as e:
         print(f"读取Excel文件失败: {e}")
         return None

    # 检查评论列是否存在
    if column_name not in df.columns:
        print(f"错误：列 '{column_name}' 在文件中未找到。可用的列: {df.columns.tolist()}")
        return None

    # 处理空评论 - 过滤掉空评论，只将非空评论送入模型预测
    # 获取非空评论的原始索引列表和文本列表
    non_empty_original_indices = [] # <-- 新增：存储非空评论在原始DataFrame中的索引
    non_empty_comments = []         # <-- 存储非空评论的文本
    for original_idx, text in enumerate(df[column_name]):
        comment_text = str(text).strip()
        if comment_text: # 如果评论不为空或只包含空白字符
            non_empty_original_indices.append(original_idx) # 记录原始索引
            non_empty_comments.append(comment_text)         # 记录评论文本

    print(f"发现 {len(non_empty_comments)} 条非空评论，将进行预测。")

    predicted_labels = [] # 用于存储预测的文本标签
    predicted_scores = [] # 用于存储预测的最高得分

    # ... (此处是使用 tokenizer 和 model 进行预测的代码，不需要修改)
    # 使用加载的 tokenizer 对非空评论进行批量编码
    if len(non_empty_comments) > 0:
        try:
            # 使用 tokenizer 编码文本，返回 PyTorch 张量
            # 使用和训练时相同的 max_length, padding 和 truncation 策略
            # 假设训练时使用的是 max_length=256
            inputs = tokenizer(
                non_empty_comments,
                padding=True,         # 填充
                truncation=True,      # 截断
                max_length=256,       # 使用训练时或你设定的最大长度
                return_tensors="pt"   # 返回 PyTorch 张量
            )

            # 将输入张量移动到模型所在的设备 (CPU 或 GPU)
            inputs = {key: val.to(model.device) for key, val in inputs.items()}

            # 将模型设置为评估模式 (会关闭 dropout 等)
            model.eval()

            # 在 torch.no_grad() 块中进行推理，不计算梯度，节省显存，加速计算
            with torch.no_grad():
                # 将编码后的输入送入模型
                outputs = model(**inputs)

            # 获取模型的输出 logits
            logits = outputs.logits

            # 将 logits 转换为概率 (可选，但 score 通常指最高概率)
            probabilities = torch.softmax(logits, dim=-1)

            # 获取每个样本最高概率对应的类别 ID
            # torch.max 返回最大值和对应的索引
            max_probs, predicted_ids = torch.max(probabilities, dim=-1)

            # 将预测结果从张量转换为 Python 列表，并移回 CPU (如果它们在 GPU 上)
            predicted_ids = predicted_ids.cpu().tolist()
            max_probs = max_probs.cpu().tolist()

            # 使用 id2label 映射将类别 ID 转换为文本标签
            predicted_labels = [id2label_map[id] for id in predicted_ids]
            predicted_scores = max_probs # 最高概率作为 score

            print("本地模型预测完成。")

        except Exception as e:
            print(f"本地模型预测失败: {e}")
            # 预测失败，保留空的 predicted_labels 和 predicted_scores 列表
            # 同时返回 None 表示整个分析过程失败，由调用者处理
            return None # 预测失败则返回 None


    else:
        print("没有非空评论需要预测。")


    # 整理结果，将分析结果与原始数据合并
    results_list = [] # 用于存储最终要输出的每行结果字典

    # 预填充结果列表，包含原始数据和默认的分析状态
    for i, row in df.iterrows():
         row_result = {
            'name': row.get('名字'), # 假设原始文件中有这些列
            'gender': row.get('性别'),
            'level': row.get('等级'),
            column_name: str(row.get(column_name, '')), # 确保评论是字符串并使用配置的列名
            'likes': row.get('点赞数'),
            'emotion': '未分析', # 默认状态
            'score': None,
            'status': '未分析'
        }
         # 稍后根据是否是空评论或预测是否成功来更新这些字段
         results_list.append(row_result)


    # 将预测结果映射回原始位置
    # predicted_labels 的长度与 non_empty_original_indices 相同
    # predicted_labels[i] 对应于原始 DataFrame 索引 non_empty_original_indices[i]
    if predicted_labels: # 只有当预测成功并有结果时才进行映射
        # 遍历预测结果及其对应的原始索引
        for i, predicted_label in enumerate(predicted_labels):
            # 获取这条预测结果对应的原始 DataFrame 索引
            original_idx = non_empty_original_indices[i] # <-- 使用正确获取的原始索引列表

            # 获取对应的得分
            predicted_score = predicted_scores[i]

            # 更新 results_list 中对应原始索引位置的条目
            results_list[original_idx]['emotion'] = predicted_label
            results_list[original_idx]['score'] = predicted_score
            results_list[original_idx]['status'] = '成功'

    # 遍历 results_list，将未被标记为“成功”的非空评论标记为“预测失败”（如果预测过程返回了None）
    # 或者将空的评论标记为“跳过”
    for i, row_result in enumerate(results_list):
        original_comment_text = str(df.iloc[i].get(column_name, '')).strip()
        if not original_comment_text:
            row_result['emotion'] = '空评论'
            row_result['status'] = '跳过'
        elif row_result['status'] == '未分析':
             # 如果是非空评论，但在预测结果映射阶段没有被标记为“成功”
             # 这通常意味着预测函数本身返回了None（发生了预测错误）
             row_result['status'] = '预测失败'
             row_result['emotion'] = '预测失败' # 或者保持 '未分析'

    return results_list

# --- 主程序执行部分 --- (保持不变)
# ... (你的主程序调用部分)
if __name__ == "__main__":
    # 调用函数进行分析，传递加载好的 tokenizer, model 和 id2label
    analysis_results = analyze_sentiments_from_excel_batch(
        excel_file_path,
        comment_column_name,
        tokenizer, # <-- 传递 tokenizer
        model,     # <-- 传递 model
        id2label_map # <-- 传递 id2label 映射
    )

    # 如果分析成功
    if analysis_results is not None:
        # 将结果列表转换为pandas DataFrame
        output_df = pd.DataFrame(analysis_results)

        # 保存结果到新的Excel文件
        try:
            # 使用 openpyxl 引擎保存为 .xlsx 格式
            output_df.to_excel(output_file_name, index=False, engine='openpyxl')
            print(f"详细分析结果已保存到 '{output_file_name}'")
        except Exception as e:
            print(f"保存文件失败: {e}")
            print("请确保文件未被占用或检查写入权限。")

    print("\n脚本执行完毕。")