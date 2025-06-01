# 🎯 Bilibili Comment Sentiment Analysis System (Fine-tuned BERT-based)

## Project Overview

This project presents a Bilibili-specific sentiment analysis system based on a fine-tuned BERT model. It includes a full pipeline from data collection to training and visualization. The system is optimized for the unique characteristics of Bilibili comments and supports accurate binary classification (positive/negative), with visualization such as word clouds.

🔗 **Model on Hugging Face**: [blank02/Bilibili-comment-fine-tuning-BERT](https://huggingface.co/blank02/Bilibili-comment-fine-tuning-BERT)

## Key Features

* **Domain-optimized model**: Fine-tuned from `chinese-bert-wwm-ext`, tailored for the style and slang of Bilibili comments.
* **End-to-end pipeline**: Covers data crawling → cleaning → labeling → training → visualization.
* **High performance**: Achieves 92.6% accuracy on Bilibili-specific dataset (a 7.2% improvement over base BERT).
* **Web UI**: Includes web-based interface for visualizing sentiment results and generating word clouds.

## Fine-tuning Details

### Base Model

[`chinese-bert-wwm-ext`](https://huggingface.co/hfl/chinese-bert-wwm-ext) – Whole Word Masking BERT for Chinese

### Performance Comparison

| Metric         | Base BERT     | Fine-tuned Model  | Improvement |
| -------------- | ------------- | ----------------- | ----------- |
| Accuracy       | 85.4%         | **92.6%**         | ↑ 7.2%      |
| F1 Score       | 0.83          | **0.91**          | ↑ 9.6%      |
| Inference Time | 38ms/instance | **22ms/instance** | ↓ 42.1%     |

### Optimization Techniques

1. Dynamic learning rate scheduling (peak at 2e-5)
2. Layer-wise learning rate decay (top-layer decay factor: 0.8)
3. Adversarial training using FGM
4. Early stopping (patience = 3)

## Project Structure

```
.
├── main_code/                    # Core scripts
│   ├── Data_crawling.py         # Bilibili comment crawler
│   ├── Data_cleaning.py         # Data cleaning
│   ├── bert_analysis.py         # Sentiment analysis module
│   ├── Word_cloud_image_generation.py  # Word cloud generator
│   └── main_file.py             # Web interface with Gradio/Flask
├── cookie.txt                   # Bilibili cookie settings
├── requirements.txt             # Dependency list
└── model/                       # Fine-tuned BERT model files
```

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Bilibili Cookie

1. Paste your valid Bilibili cookie into `cookie.txt`
2. Format example: `SESSDATA=xxx; bili_jct=xxx`

### Run Workflow

```bash
# 1. Crawl comment data (example BV ID: BV1xx411x7xx)
python Data_crawling.py --video_id BV1xx411x7xx

# 2. Clean data
python Data_cleaning.py

# 3. Sentiment analysis
python bert_analysis.py

# 4. Start web interface
python main_file.py
```

## Demo

### Data Crawling Interface

![Screenshot](media/crawling_screenshot.png)

### Sentiment Classification Result

```json
{
  "comment": "This creator’s content is amazing!",
  "sentiment": "positive",
  "confidence": 0.963
}
```

### Word Cloud Visualization

![Word Cloud](media/wordcloud_example.png)

## Tech Stack

* **Deep Learning**: PyTorch + Huggingface Transformers
* **Data Processing**: Pandas + Jieba
* **Visualization**: WordCloud + Matplotlib
* **Web UI**: Flask / Gradio

## FAQ

**Q: How can I get the Bilibili Cookie?**
A: Log into Bilibili, open DevTools (F12), go to the "Network" tab and find your session cookie.

**Q: What sentiment classes does the model support?**
A: Currently supports binary classification: positive / negative

> Feel free to open an issue if you have questions or suggestions.
