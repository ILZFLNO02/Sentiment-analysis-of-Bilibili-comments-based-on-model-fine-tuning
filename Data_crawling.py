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

# def crawl_data(bv_number):
#     headers = {
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
#         # 自己电脑的user-agant
#         'referer': 'https://www.bilibili.com/video/',
#         # 网址
#         'cookie': "buvid4=8D4A2ADE-CB95-88DF-FD3B-CC9F77BE244869063-022012421-Vk7oLekZ8O%2BWwDC%2BideQ6A%3D%3D; header_theme_version=CLOSE; enable_web_push=DISABLE; LIVE_BUVID=AUTO8617093666395399; buvid_fp=742d1522a279e233ccc0138e20571bfc; FEED_LIVE_VERSION=V_WATCHLATER_PIP_WINDOW3; CURRENT_BLACKGAP=0; hit-dyn-v2=1; CURRENT_QUALITY=80; is-2022-channel=1; _uuid=9254D896-12710-2A22-6410C-6A56C788799863056infoc; DedeUserID=347760015; DedeUserID__ckMd5=b3e098a82a04b457; PVID=3; buvid3=AAF79126-1DA9-8B4A-59F3-E32F7485E4B982916infoc; b_nut=1736682182; rpdid=|(J|)Y~Ru)|~0J'u~JmYklkk~; fingerprint=5decd515eea056e6f18864bc721b8fc0; enable_feed_channel=ENABLE; bp_t_offset_347760015=1044087535837380608; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDIzNjAzNjMsImlhdCI6MTc0MjEwMTEwMywicGx0IjotMX0.fbW-zCSgduGSg170p1VQhNDD5iKRU_QJEJDpup2hiS0; bili_ticket_expires=1742360303; SESSDATA=0266dedc%2C1757751098%2C1007d%2A31CjB41oEdKqiUzZagdFRRNIITu8eSGq1J6Ef2PUO_iwAC2xP0047m03XxaNQQ511dkqASVmJDc1E2Rk5RanhSTDBfOHgyMUtHRE9meWtBWXc4MV9lYzFtYlVEVlBfNXRrRktTZ1Q0bmhvdXhmSzY1T3VlOVJDcFVjY01lLXJHUjRTaVc2UHNLSDF3IIEC; bili_jct=2369d4e04b7dbe48be089ad0175a6cb3; b_lsid=710BA53B5_195A6F4E8A4; sid=7ovxl346; CURRENT_FNVAL=4048; home_feed_column=4; browser_resolution=120-571" #
#         # 输入自己的cookie
#
#     }

    for page in range(1, 2):
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
    workbook.save(r"评论信息.xls")
crawl_data("BV1Z55VznEdq") # 你可以保留或注释掉这行测试代码
