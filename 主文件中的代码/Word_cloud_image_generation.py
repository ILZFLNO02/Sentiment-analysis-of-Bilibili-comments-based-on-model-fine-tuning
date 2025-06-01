import pandas as pd
from wordcloud import WordCloud
import jieba
import matplotlib.pyplot as plt

def generate_word_cloud(filepath, stopwords_path, mask_image_path, save_image_path):
    # 读取Excel文件
    data = pd.read_excel(filepath, names=["名字", "性别", "等级", "评论内容", "点赞数"], usecols=[0, 1, 2, 3, 4])

    # 读取停用词列表
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = f.read().splitlines()

    # 合并所有评论内容为一个字符串
    all_comments = ' '.join(data["评论内容"].astype(str))

    # 分词并去除停用词
    data_cut = jieba.lcut(all_comments)
    data_after = [i for i in data_cut if i not in stopwords]

    # 统计词频
    word_freq = pd.Series(data_after).value_counts()

    # 生成词云图
    mask = plt.imread(mask_image_path)
    wc = WordCloud(scale=10,
                  font_path='C:/Windows/Fonts/STXINGKA.TTF',
                  background_color="white",
                  mask=mask)
    wc.generate_from_frequencies(word_freq.to_dict())

    # 保存并关闭图形
    plt.figure(figsize=(20, 20))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(save_image_path, bbox_inches='tight', pad_inches=0)
    plt.close()  # 关闭图形避免内存泄漏

    return save_image_path  # 返回保存路径