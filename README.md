以下是根据你项目实际内容优化后的 `README.md` 文本，结构清晰、用词简洁、专业度高，并用 Markdown 语法排版，适合作为开源项目首页说明文档：

---

# 🎯 Sentiment Analysis of Bilibili Comments Based on Model Fine-Tuning

本项目为青海民族大学本科毕业设计，旨在构建一个**基于情感分析的B站创作者画像系统**，通过**微调中文预训练模型（chinese-bert-wwm-ext）**，实现对用户评论的高精度情感分析，并辅助平台构建健康社区生态。

## 🧠 项目简介

本项目构建了一个面向B站视频评论的情感分析与可视化系统，主要包括以下几个核心模块：

* 🔍 **评论数据采集**：通过B站 API 结合用户 Cookie，批量抓取视频评论；
* 🧼 **数据清洗与标注**：自动清洗噪声评论，并结合预训练模型与人工校对构建高质量数据集；
* 🤖 **模型微调与训练**：基于 `chinese-bert-wwm-ext` 模型进行迁移学习，提升评论情感分类准确率；
* 📈 **情感可视化与创作者画像生成**：生成情感分析图表、词云及创作者综合评估报告；
* 🌐 **Web页面演示**：通过 Gradio 构建用户友好的网页交互界面。

## 🏗️ 项目结构

```bash
主目录/
│
├── Data_crawling.py               # B站评论爬虫脚本（需配合cookie.txt）
├── Data_cleaning.py               # 数据清洗与预处理
├── bert_analysis.py               # 微调后的BERT情感分析主程序
├── Word_cloud_image_generation.py# 词云图生成
├── main_file.py                   # Web 页面入口（基于 Gradio）
├── cookie.txt                     # 用户自己的 B站 cookie
├── requirements.txt              # 运行所需Python依赖
```

## 🧪 模型说明

* **基座模型**：[`chinese-bert-wwm-ext`](https://huggingface.co/hfl/chinese-bert-wwm-ext)（由哈工大讯飞联合实验室发布）

* **微调方法**：

  * 采用约 3000 条人工与半自动标注评论数据集；
  * 使用 HuggingFace Transformers，设置分类为三类（正向、中立、负向）；
  * 微调过程使用 `Trainer` 接口，训练7轮后模型准确率达 **80.7%**，F1 分数为 **0.802**；
  * 模型对高置信度预测样本占比提升至 **82.9%**，相比原模型（59.2%）大幅优化。

* **模型下载**：[blank02/Bilibili-comment-fine-tuning-BERT](https://huggingface.co/blank02/Bilibili-comment-fine-tuning-BERT)
  下载后将模型目录放置在与主代码目录同级位置。
* **优化策略**
  * 动态学习率调度（峰值2e-5）
  * 分层学习率衰减（顶层衰减系数0.8）
  * 对抗训练（FGM方法）
  * 早停策略（patience=3）

## 📊 效果展示

* **情感分布图**：展示不同性别用户对某创作者评论区情绪的分布；
* **高频词词云**：突出评论区常见关键词，如“好听”、“喜欢”、“春晚”等；
* **创作者评估报告**：基于点赞加权的情感得分，划分创作者为强烈推荐、正向、中立、负向等类型。

## ✅ 使用说明

1. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```
2. 将你的 Cookie 复制到 `cookie.txt`；
3. 运行 `main_file.py` 启动 Web 页面进行交互；
4. 如需重新微调模型，请运行 `bert_analysis.py` 并使用自己的数据集。

## 💡 项目特色

* 🔧 **中文BERT微调**：针对B站网络评论优化，适应表情、网络流行语、讽刺等复杂语义；
* 📈 **可视化友好**：结合情感分析结果生成词云图和统计图，便于结果解读；
* 🧩 **创作者画像构建**：为内容管理提供量化参考，辅助平台治理与推荐优化。


## ？常见问题
Q: 如何获取B站Cookie？  
A: 登录B站后，在开发者工具（F12）的Network标签页获取Cookie值

Q: 模型支持哪些情感类别？  
A: 当前版本支持二分类：积极(positive)/消极(negative)



如项目对你有帮助，欢迎 Star 🌟 或留言交流！

---

如你需要我帮你配套生成 HuggingFace 或 GitHub 上的项目描述模板、模型卡 (`README.md` for model card)，也可以继续告诉我。
