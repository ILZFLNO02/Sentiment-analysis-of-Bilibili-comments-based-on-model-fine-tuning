import pandas as pd
import re
# from tkinter import messagebox  #  <--  注释掉或删除 tkinter messagebox 的导入，因为不再需要

def clean_chinese_characters(filepath):
    # 定义一个函数来保留中文字符
    def keep_chinese_characters(text):
        # 使用正则表达式匹配中文字符
        chinese_characters = re.findall(r'[\u4e00-\u9fff]+', text)
        # 读取停用词文件
        with open('hit_stopwords.txt', 'r', encoding='utf-8') as f:
            stopwords = [word.strip() for word in f.readlines()]
        # 将中文字符分词并去除停用词
        words = [word for word in ''.join(chinese_characters).split() if word not in stopwords]
        # 将处理后的词语连接起来
        return ''.join(words)
    # 读取Excel文件
    data = pd.read_excel(filepath)
    # 删除整行重复的评论信息
    data.drop_duplicates(subset='评论内容', keep='first', inplace=True)
    # 清理'评论内容'列，只保留中文字符
    data['评论内容'] = data['评论内容'].apply(keep_chinese_characters)
    # 将清理后的DataFrame写入新的Excel文件
    cleaned_filepath = filepath.replace('.xls', '_清洗去重后.xlsx')
    data.to_excel(cleaned_filepath, index=False)
    return cleaned_filepath

#clean_chinese_characters("评论信息.xls") #  你可以保留或注释掉这行测试代码