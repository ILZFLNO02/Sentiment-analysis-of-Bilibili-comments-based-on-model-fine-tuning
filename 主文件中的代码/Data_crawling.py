import requests
import json
import xlwt
comment_list = []
sex_list = []
like_list = []
level_list = []
name_list = []

import os
# 读取同一文件夹下的 cookie.txt 文件内容
cookie_file_path = 'cookie.txt'  # 文件名
if os.path.exists(cookie_file_path):
    with open(cookie_file_path, 'r', encoding='utf-8') as file:
        cookie_value = file.read().strip()  # 读取文件内容并去除首尾空白字符
else:
    raise FileNotFoundError(f"文件 {cookie_file_path} 不存在，请确保文件已正确放置在当前文件夹中。")
def crawl_data(bv_number):
    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
    # 自己电脑的user-agent
    'referer': 'https://www.bilibili.com/video/',  # 网址
    'cookie': cookie_value  # 从文件中读取的 cookie 值
}
    for page in range(1, 11):
        url = f'https://api.bilibili.com/x/v2/reply/main?jsonp=jsonp&next={page}&type=1&oid={bv_number}&sort=2&p={page}'
        response = requests.get(url=url, headers=headers).text
        re_data = json.loads(response)
        if re_data['data']['replies'] != None :
            for i in re_data["data"]['replies']:
                comment = i["content"]['message']
                name = i["member"]['uname']
                like = i["like"]
                level = i['member']['level_info']['current_level']
                sex = i["member"]['sex']

                comment_list.append(comment)
                sex_list.append(sex)
                like_list.append(like)
                level_list.append(level)
                name_list.append(name)

    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet("test_sheet")
    worksheet.write(0, 0, label='名字')
    worksheet.write(0, 1, label='性别')
    worksheet.write(0, 2, label='等级')
    worksheet.write(0, 3, label='评论内容')
    worksheet.write(0, 4, label='点赞数')
    for i in range(len(name_list)):
        worksheet.write(i + 1, 0, label=name_list[i])
        worksheet.write(i + 1, 1, label=sex_list[i])
        worksheet.write(i + 1, 2, label=level_list[i])
        worksheet.write(i + 1, 3, label=comment_list[i])
        worksheet.write(i + 1, 4, label=like_list[i])
    workbook.save(r"评论信息.xlsx")
#crawl_data("BV1Z55VznEdq") # 你可以保留或注释掉这行测试代码
