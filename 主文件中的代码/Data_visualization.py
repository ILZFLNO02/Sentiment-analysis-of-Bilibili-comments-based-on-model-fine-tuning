import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Page
from pyecharts.faker import Faker

def visualize_data(filepath, image_path=None, output_excel_path="创作者评估报告.xlsx"):
    # 读取数据
    data = pd.read_excel(filepath, names=["名字", "性别", "等级", "评论内容", "点赞数", "BERT标签" ],
                        usecols=[0, 1, 2, 3, 4, 5])
    sentiment_data = pd.read_excel(filepath, names=["性别", "BERT标签"],
                                  usecols=[1, 5])
    # 重新加载BERT标签输出结果数据
    analysis_sentiment_data = pd.read_excel(filepath)
    # 计算该创作者所有视频的正向和负向评论数量
    creator_sentiment_counts = analysis_sentiment_data['BERT标签'].value_counts()
    # 计算正向和负向评论的比例
    creator_positive_ratio = creator_sentiment_counts.get('正向', 0) / len(analysis_sentiment_data)
    creator_negative_ratio = creator_sentiment_counts.get('负向', 0) / len(analysis_sentiment_data)
    # 分析不同性别用户对该创作者内容的BERT标签反应
    # 计算每个性别的正向和负向评论数量
    gender_sentiment_counts = analysis_sentiment_data.groupby('性别')['BERT标签'].value_counts().unstack().fillna(0)
    # 计算每个性别的正向和负向评论的比例
    gender_positive_ratio = gender_sentiment_counts['正向'] / gender_sentiment_counts.sum(axis=1)
    gender_negative_ratio = gender_sentiment_counts['负向'] / gender_sentiment_counts.sum(axis=1)
    # 整理创作者分析画像文本
    creator_analysis_text = f"""
    <div style="margin-top: 30px; border-top: 2px solid #ccc; padding-top: 20px;">
        <h2>创作者整体情感分析画像</h2>
        <p><strong>正向评论比例：</strong> 正向评论占比为 {creator_positive_ratio:.2%}</p>
        <p><strong>负向评论比例：</strong> 负向评论占比为 {creator_negative_ratio:.2%}</p>
        <h3>不同性别用户情感反应分析</h3>
        <p><strong>正向评论比例：</strong></p>
        <ul>
            <li>保密用户：{gender_positive_ratio.get('保密', 'N/A'):.2%}</li>
            <li>女性用户：{gender_positive_ratio.get('女', 'N/A'):.2%}</li>
            <li>男性用户：{gender_positive_ratio.get('男', 'N/A'):.2%}</li>
        </ul>
        <p><strong>负向评论比例：</strong></p>
        <ul>
            <li>保密用户：{gender_negative_ratio.get('保密', 'N/A'):.2%}</li>
            <li>女性用户：{gender_negative_ratio.get('女', 'N/A'):.2%}</li>
            <li>男性用户：{gender_negative_ratio.get('男', 'N/A'):.2%}</li>
        </ul>
    </div>
    """
    # ----------------------  创作者分析画像代码 (到这里结束) ----------------------


    # ----------------------  创作者综合评估代码 (从这里开始添加) ----------------------
    def evaluate_creator_sentiment(df, output_file="创作者综合评估结果.xlsx"): # 内部函数，接收 DataFrame
        # 处理点赞数字段
        df['点赞数'] = pd.to_numeric(df['点赞数'], errors='coerce').fillna(0).astype(int)

        # 筛选点赞数TOP100的评论
        top_100 = df.nlargest(100, '点赞数')

        # 分离正向/负向评论（中向评论不参与计算）
        positive = top_100[top_100['BERT标签'] == '正向']
        negative = top_100[top_100['BERT标签'] == '负向']

        # 采用BERT标签后的加权得分（正向/负向评论点赞数之和）
        positive_score = positive['点赞数'].sum()
        negative_score = negative['点赞数'].sum()

        # 计算评论比例
        total = len(positive) + len(negative)
        positive_ratio = len(positive) / total if total > 0 else 0
        negative_ratio = len(negative) / total if total > 0 else 0

        # 综合评分公式（可调整系数）
        score_ratio = positive_score / (positive_score + negative_score) if (positive_score + negative_score) > 0 else 0
        comprehensive_score = 0.7 * score_ratio + 0.3 * positive_ratio  # 70%权重给得分占比，30%权重给数量比例

        # 综合评判
        if comprehensive_score > 0.7:
            creator_type = "强烈推荐创作者"
        elif comprehensive_score > 0.6:
            creator_type = "正向创作者"
        elif comprehensive_score > 0.4:
            creator_type = "中立创作者"
        else:
            creator_type = "负向创作者"
            
        # 提取高频词
        import jieba
        import re
        
        # 读取停用词列表
        try:
            with open("hit_stopwords.txt", 'r', encoding='utf-8') as f:
                stopwords = f.read().splitlines()
        except:
            stopwords = []
            
        # 合并所有评论内容为一个字符串
        all_comments = ' '.join(df["评论内容"].astype(str))
        
        # 使用正则表达式过滤掉特殊字符和数字
        all_comments = re.sub(r'[\[\](){}@,.?!;:"\'\d]+', '', all_comments)
        
        # 分词并去除停用词
        data_cut = jieba.lcut(all_comments)
        data_after = [i for i in data_cut if i not in stopwords and len(i.strip()) > 1]
        
        # 统计词频
        word_freq = pd.Series(data_after).value_counts().head(10)
        top_words = "、".join([f"{word}({count})" for word, count in word_freq.items()])

        # 生成详细报告
        report = f"""
        <div style="margin-top: 30px; border-top: 2px solid #ccc; padding-top: 20px;">
            <h2>创作者综合评估报告</h2>
            <p><strong>* 核心指标分析 *</strong></p>
            <ul>
                <li>加权正向得分（正向评论点赞数之和）：{positive_score:.2f}</li>
                <li>加权负向得分（负向评论点赞数之和）：{negative_score:.2f}</li>
                <li>正向评论占比：{positive_ratio:.2%}</li>
                <li>综合推荐指数：{comprehensive_score:.2f}/1.0</li>
            </ul>
            <p><strong>* 创作者类型 *</strong></p>
            <p>{creator_type}</p>
            <p>创作者高频词为：{top_words}</p>
            <h3>【评分逻辑说明】</h3>
            <ol>
                <li>TOP100高赞评论加权：正向评论点赞数之和，负向评论点赞数之和</li>
                <li>综合评分 = 70%×正向得分占比 + 30%×正向评论数量占比</li>
                <li>评价阈值：>0.7强烈推荐，>0.6正向，>0.4中立，≤0.4负向</li>
            </ol>
        </div>
        """

        # 保存结果到 Excel
        result_df = pd.DataFrame({
            '指标': ['正向得分', '负向得分', '正向评论数', '负向评论数', '综合评分', '创作者类型'],
            '数值': [positive_score, negative_score, len(positive), len(negative), comprehensive_score, creator_type],
            '说明': [
                "正向评论点赞数之和",
                "负向评论点赞数之和",
                "TOP100中正向评论数量",
                "TOP100中负向评论数量",
                "0.7×得分占比 + 0.3×数量占比",
                "基于综合评分阈值判定"
            ]
        })

        with pd.ExcelWriter(output_file) as writer:
            result_df.to_excel(writer, sheet_name='评估结果', index=False)
            pd.DataFrame({'报告内容': [report]}).to_excel(writer, sheet_name='分析报告', index=False)

        return report, output_file # 返回报告文本和 Excel 文件路径


    evaluation_report_text, excel_output_path = evaluate_creator_sentiment(analysis_sentiment_data, output_excel_path) # 调用评估函数
    creator_analysis_text += evaluation_report_text # 将评估报告文本添加到创作者分析画像文本中
    # ----------------------  创作者综合评估代码 (到这里结束) ----------------------


    # 创建Page对象
    page = Page(layout=Page.SimplePageLayout, page_title="B站评论数据可视化分析")  # 简单垂直布局, 设置HTML页面标题

    # 点赞数Top20的评论柱状图
    df1 = data.sort_values(by="点赞数", ascending=False).head(20)
    bar = (
        Bar()
        .add_xaxis(df1["评论内容"].to_list())
        .add_yaxis("点赞数", df1["点赞数"].to_list(), color=Faker.rand_color())
        .set_global_opts(
            title_opts=opts.TitleOpts(title="评论热度Top20"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
        )
    )
    page.add(bar)

    # 用户等级分布饼图
    level_pie = (
        Pie()
        .add(
            "",
            [list(z) for z in zip([str(i) for i in range(7)],
                                 data.等级.value_counts().sort_index(ascending=False).to_list())],
            radius=["40%", "75%"]
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="用户等级分布"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%")
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    page.add(level_pie)

    # 用户性别分布饼图
    gender_pie = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(["男", "女", "保密"],
                                 data.性别.value_counts().sort_index(ascending=False).to_list())],
            radius=["40%", "75%"]
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="用户性别分布"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%")
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    page.add(gender_pie)

    # 情感倾向饼图（分性别）
    for gender in ["男", "女", "保密"]:
        gender_sentiment = sentiment_data[sentiment_data["性别"] == gender]["BERT标签"].value_counts()
        sentiment_pie = (
            Pie()
            .add(
                "",
                [list(z) for z in zip(["积极", "中性", "消极"], gender_sentiment.tolist())],
                radius=["40%", "75%"]
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"{gender}性别情感倾向分布"),
                legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%")
            )
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )
        page.add(sentiment_pie)

    # 统一渲染到单个HTML文件
    page.render("所有可视化图表.html")

    # 将创作者分析文本追加到 HTML 文件末尾
    with open("所有可视化图表.html", "r+", encoding='utf-8') as f:
        html_content = f.read()
        # 在 </body> 标签前插入创作者分析文本
        html_content = html_content.replace("</body>", creator_analysis_text + "</body>")
        f.seek(0) # 将文件指针移动到文件开头
        f.write(html_content) # 重新写入修改后的HTML内容
        f.truncate() # 移除文件剩余部分


    # 如果需要生成图片 (这部分代码可以根据您的需求保留或移除)
    if image_path:
        import os
        from selenium import webdriver
        from PIL import Image

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get("file://" + os.path.abspath("所有可视化图表.html"))
        driver.save_screenshot(image_path)
        driver.quit()
        img = Image.open(image_path)
        img = img.crop(img.getbbox())  # 裁剪图片
        img.save(image_path)

# 使用示例
#visualize_data("情感输出结果_bert.xlsx", output_excel_path="创作者评估报告_bert.xlsx") #  同时指定 Excel 输出路径