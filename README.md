# Sentiment-analysis-of-Bilibili-comments-based-on-model-fine-tuning
我的大学毕业设计，这是一个以chinese-bert-wwm-ext为基座模型微调后的，更适用于b站评论的情感分析模型。包含数据爬取、数据标注、模型微调、以及后面的可视化部分，如果对你有帮助，感谢点赞。
# 文件说明
主文件代码目录 包含数据爬取（Data_crawling.py）、数据清洗（Data_cleaning.py）、情感分析（bert_analysis.py）、词云图生成（Word_cloud_image_generation.py）、web页面演示的功能（main_file.py）
数据爬取.py这个文件主要实现：通过b站api来爬取多个视频下的评论
cookie.txt文件放的是你自己的的cookie
整个文件逻辑应该是完善的 只要吧你自己的cookie放上去 安装对应库就能运行
对应的需求库在requirements.txt中。
如有运行问题，请留言
