import gradio as gr
import Data_crawling
import Data_cleaning
import bert_analysis
import Word_cloud_image_generation
import Data_visualization
import os
#数据爬取
def crawl_data_gradio(bv_number):
    Data_crawling.crawl_data(bv_number)
    return "数据抓取完成"  # 返回文本信息，Gradio 将在界面上显示
#数据清洗
def clean_data_gradio():
    filepath = "评论信息.xls"
    cleaned_filepath = Data_cleaning.clean_chinese_characters(filepath)
    return f"清洗后的文件保存为：{cleaned_filepath}" # 返回清洗后文件路径
#情感分析
def analyse_data_gradio():
    filepath = "评论信息.xlsx"
    save_file = "情感输出结果_bert.xlsx"
    model_path = "e:/bilibili_train/bert_train"
    analyse_filepath = bert_analysis.analyze_sentiment(filepath, save_file, model_path)
    return f"分析后的文件保存为：{analyse_filepath}" # 返回情感分析结果文件路径
#词云图生成
def generate_word_cloud_gradio():
    image_path = "word_cloud_image.png"
    mask_image_path = "mask.png"
    # 确保返回图片路径
    return Word_cloud_image_generation.generate_word_cloud(
        filepath="评论信息_清洗去重后.xlsx",
        stopwords_path="hit_stopwords.txt",
        mask_image_path=mask_image_path,
        save_image_path=image_path
    )
def visualize_data_gradio():
    html_path = "所有可视化图表.html"
    Data_visualization.visualize_data("情感输出结果_bert.xlsx")
    #  不再读取 HTML 文件内容，直接返回文字提示信息
    return f"数据可视化图表已生成并保存到本地文件：{html_path}，请在本地文件中查看。"

# 使用 Blocks API 创建 Gradio 界面
with gr.Blocks(title="B站评论分析 Web 应用") as demo:
    gr.Markdown("""
    # B站评论分析 Web 应用
    这是一个用于 B 站评论数据分析的 Web 应用。
    请输入要爬取视频的 BV 号，然后点击下方按钮执行数据爬取、清洗、情感分析、词云图生成和数据可视化等操作。
    """)

    bv_input = gr.Textbox(label="输入要爬取视频的BV号")
    output_info = gr.Markdown("请点击下方按钮执行相应操作")
    image_output_wordcloud = gr.Image(width=1000, height=700)
    # 使用 gr.Markdown 组件显示 HTML 内容，而不是 gr.HTML
    html_output = gr.Markdown()

    with gr.Row():
        crawl_button = gr.Button("开始爬取")
        clean_button = gr.Button("清洗数据")
        analyse_button = gr.Button("情感分析")
        wordcloud_button = gr.Button("词云图生成")
        visualize_button = gr.Button("生成创作者画像")

    crawl_button.click(crawl_data_gradio, inputs=bv_input, outputs=output_info)
    clean_button.click(clean_data_gradio, inputs=[], outputs=output_info)
    analyse_button.click(analyse_data_gradio, inputs=[], outputs=output_info)
    wordcloud_button.click(generate_word_cloud_gradio, inputs=[], outputs=image_output_wordcloud)
    # 修改可视化按钮的输出目标为 html_output，并确保 outputs 是 html_output 组件
    visualize_button.click(
        visualize_data_gradio,
        inputs=[],
        outputs=html_output
    )

if __name__ == "__main__":
    demo.launch(share=False)