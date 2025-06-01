import pandas as pd

# 设置您的Excel文件路径
# file_path = '评论情感分析结果_三分类_人工纠错.xlsx' # 请将这里替换成您的实际文件名和路径
file_path = '评论情感分析结果_三分类_本地模型批量预测.xlsx' # 请将这里替换成您的实际文件名和路径
try:
    # 读取Excel文件
    df = pd.read_excel(file_path)

    # 确保存在 'score' 列
    if 'score' not in df.columns:
        print(f"错误：Excel文件 '{file_path}' 中未找到 'score' 列。请检查列名是否正确。")
    else:
        # 获取 'score' 列的数据
        scores = df['score']

        # 定义分数区间 (bins)
        # bins的边界是 [0, 0.1, 0.2, ..., 0.9, 1.0]
        # right=False 表示区间是左闭右开 [0, 0.1), [0.1, 0.2) ... [0.9, 1.0)
        # 如果您希望区间是左开右闭 (0, 0.1], (0.1, 0.2] ... (0.9, 1.0]，请设置 right=True
        # 对于0到1的得分，通常包含1，所以定义bins到1.01，或使用right=True包含右边界
        bins = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        # 如果需要包含1.0的区间，可以稍微调整bins的最后一个边界或使用right=True
        # bins = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.01] # 稍微超过1.0以包含1.0

        # 使用pd.cut将分数分配到对应的区间
        # labels=False 会直接返回区间的整数索引
        # include_lowest=True 包含最低的边界（即0.0）
        score_bins = pd.cut(scores, bins=bins, right=True, include_lowest=True) # right=True 包含右边界，这样 1.0 会被包含在最后一个区间

        # 计算每个区间的数量
        bin_counts = score_bins.value_counts().sort_index()

        # 计算总分数数量（排除可能的NaN值）
        total_scores = scores.count() # count()方法会自动排除NaN值

        # 计算每个区间的占比
        bin_proportions = bin_counts / total_scores

        # 打印结果
        print("分数区间分布及占比：")
        print("-" * 30)
        for interval, count in bin_counts.items():
             proportion = bin_proportions.get(interval, 0) # 使用.get确保即使没有值也不会报错
             print(f"{interval}: 数量 = {count}, 占比 = {proportion:.2%}") # 格式化为百分比

        print("-" * 30)
        print(f"总有效分数数量: {total_scores}")


except FileNotFoundError:
    print(f"错误：未找到文件 '{file_path}'。请检查文件路径是否正确。")
except Exception as e:
    print(f"处理过程中发生错误: {e}")