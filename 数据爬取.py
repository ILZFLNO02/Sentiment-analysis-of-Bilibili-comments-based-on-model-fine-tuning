import requests
import json
import xlwt
import xlrd # 导入 xlrd 用于读取现有Excel文件
from xlutils.copy import copy # 导入 copy 用于复制可读的workbook到可写的workbook
import os
import time
import random

# 读取同一文件夹下的 cookie.txt 文件内容
cookie_file_path = 'cookie.txt'  # 文件名
cookie_value = "" # 初始化 cookie_value
if os.path.exists(cookie_file_path):
    with open(cookie_file_path, 'r', encoding='utf-8') as file:
        cookie_value = file.read().strip()  # 读取文件内容并去除首尾空白字符
    if not cookie_value:
        raise ValueError(f"文件 {cookie_file_path} 内容为空，请确保cookie已正确写入。")
else:
    raise FileNotFoundError(f"文件 {cookie_file_path} 不存在，请确保文件已正确放置在当前文件夹中。")

def crawl_data_and_append(bv_number):
    """
    爬取指定BV号视频的评论数据，并追加到Excel文件。
    Args:
        bv_number: 视频的BV号 (字符串)。
    """

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'referer': f'https://www.bilibili.com/video/{bv_number}',
        'cookie': cookie_value,
        'Accept': 'application/json, text/plain, */*',  # B站API常见Accept
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',  # 根据你浏览器设置调整
        'Connection': 'keep-alive'  # 保持连接
    }
    # 使用局部列表存储当前BV号爬取的数据
    current_comment_list = []
    current_sex_list = []
    current_like_list = []
    current_level_list = []
    current_name_list = []

    # 原代码只爬取了第一页 (range(1, 2))，这里保留一致。
    # 如果需要爬取更多页，修改 range 的范围即可。
    # 注意：爬取多页时，start_row 的计算方式不受影响，数据会依次追加。
    for page in range(1, 6): # 示例只爬取第一页
        time.sleep(random.uniform(3, 15))
        url = f'https://api.bilibili.com/x/v2/reply/main?jsonp=jsonp&next={page}&type=1&oid={get_oid_from_bv(bv_number)}&sort=2&p={page}' # 需要oid，调用函数转换
        print(f"正在爬取 BV号 {bv_number} 的第 {page} 页评论...")
        try:
            response = requests.get(url=url, headers=headers)
            response.raise_for_status() # 检查HTTP请求是否成功
            re_data = response.json()

            if re_data['code'] != 0:
                 print(f"爬取 BV号 {bv_number} 第 {page} 页评论时API返回错误：{re_data.get('message', '未知错误')}")
                 # 尝试使用BV号作为oid，有时候API也支持
                 url_fallback = f'https://api.bilibili.com/x/v2/reply/main?jsonp=jsonp&next={page}&type=1&oid={bv_number}&sort=2&p={page}'
                 print(f"尝试使用BV号 {bv_number} 作为oid重新爬取...")
                 response_fallback = requests.get(url=url_fallback, headers=headers)
                 response_fallback.raise_for_status()
                 re_data_fallback = response_fallback.json()
                 if re_data_fallback['code'] == 0:
                     re_data = re_data_fallback
                     print("成功使用BV号作为oid。")
                 else:
                     print(f"使用BV号作为oid也失败：{re_data_fallback.get('message', '未知错误')}")
                     continue # 跳过当前页

            if re_data['data']['replies'] is not None:
                for reply in re_data["data"]['replies']:
                    comment = reply["content"]['message']
                    name = reply["member"]['uname']
                    like = reply["like"]
                    level = reply['member']['level_info']['current_level']
                    sex = reply["member"]['sex']

                    current_comment_list.append(comment)
                    current_sex_list.append(sex)
                    current_like_list.append(like)
                    current_level_list.append(level)
                    current_name_list.append(name)
            else:
                 print(f"BV号 {bv_number} 第 {page} 页没有评论数据。")

        except requests.exceptions.RequestException as e:
            print(f"请求 BV号 {bv_number} 第 {page} 页评论时发生错误: {e}")
        except json.JSONDecodeError:
             print(f"解析 BV号 {bv_number} 第 {page} 页评论响应时发生JSON解码错误。")
        except Exception as e:
             print(f"处理 BV号 {bv_number} 第 {page} 页评论数据时发生未知错误: {e}")


    # --- 追加写入Excel文件的逻辑 ---
    excel_filename = "多视频评论信息.xls"
    start_row = 0 # 新数据写入的起始行

    if os.path.exists(excel_filename):
        # 文件已存在，读取并复制
        try:
            read_workbook = xlrd.open_workbook(excel_filename)
            read_sheet = read_workbook.sheet_by_index(0)
            start_row = read_sheet.nrows # 新数据从现有数据的下一行开始写入
            write_workbook = copy(read_workbook) # 复制一个可写的workbook
            write_sheet = write_workbook.get_sheet(0) # 获取第一个sheet (假设数据都在第一个sheet)
            print(f"文件 '{excel_filename}' 已存在，新数据将从第 {start_row + 1} 行开始追加。")
        except xlrd.XLRDError as e:
            print(f"读取现有Excel文件 '{excel_filename}' 时发生错误: {e}")
            print("可能文件已损坏或格式不正确，尝试创建新文件。")
            # 如果读取失败，按文件不存在处理
            start_row = 0
            write_workbook = xlwt.Workbook(encoding='utf-8')
            write_sheet = write_workbook.add_sheet("评论信息") # 使用一致的sheet名称
            # 写入表头
            write_sheet.write(0, 0, label='名字')
            write_sheet.write(0, 1, label='性别')
            write_sheet.write(0, 2, label='等级')
            write_sheet.write(0, 3, label='评论内容')
            write_sheet.write(0, 4, label='点赞数')
            start_row = 1 # 数据从第2行（索引1）开始写
            print("创建新的Excel文件。")
    else:
        # 文件不存在，创建新文件并写入表头
        write_workbook = xlwt.Workbook(encoding='utf-8')
        write_sheet = write_workbook.add_sheet("评论信息") # 使用一致的sheet名称
        # 写入表头
        write_sheet.write(0, 0, label='名字')
        write_sheet.write(0, 1, label='性别')
        write_sheet.write(0, 2, label='等级')
        write_sheet.write(0, 3, label='评论内容')
        write_sheet.write(0, 4, label='点赞数')
        start_row = 1 # 数据从第2行（索引1）开始写
        print(f"文件 '{excel_filename}' 不存在，创建新文件。")


    # 将当前BV号的数据写入Excel
    for i in range(len(current_name_list)):
        # 写入时使用 start_row + 当前数据在列表中的索引 作为行号
        try:
            write_sheet.write(start_row + i, 0, label=current_name_list[i])
            write_sheet.write(start_row + i, 1, label=current_sex_list[i])
            write_sheet.write(start_row + i, 2, label=current_level_list[i])
            write_sheet.write(start_row + i, 3, label=current_comment_list[i])
            write_sheet.write(start_row + i, 4, label=current_like_list[i])
        except Exception as e:
            print(f"写入 BV号 {bv_number} 的第 {start_row + i} 行数据时发生错误: {e}")
            print(f"数据详情: 名字={current_name_list[i]}, 性别={current_sex_list[i]}, 等级={current_level_list[i]}, 评论={current_comment_list[i]}, 点赞={current_like_list[i]}")


    # 保存workbook，这会覆盖掉原来的文件（但已经包含了旧数据和新数据）
    try:
        write_workbook.save(excel_filename)
        print(f"BV号 {bv_number} 的 {len(current_name_list)} 条评论数据已成功追加到 '{excel_filename}'。")
    except Exception as e:
        print(f"保存Excel文件 '{excel_filename}' 时发生错误: {e}")

# 添加一个辅助函数，根据BV号获取oid
# B站评论API通常需要oid（视频的aid）而不是bv号
# 虽然有时直接用bv号作为oid也能工作，但稳妥起见还是转换一下
def get_oid_from_bv(bv_number):
    """
    根据BV号获取视频的AID (用于评论API的oid)。
    如果获取失败，返回原始BV号。
    """
    url = f"https://api.bilibili.com/x/web-interface/view/detail?bvid={bv_number}"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'cookie': cookie_value
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data['code'] == 0 and data['data'] and data['data']['View']:
            return data['data']['View']['aid']
        else:
            print(f"无法获取BV号 {bv_number} 的AID，API返回: {data.get('message', '未知错误')} 或数据结构不符。将尝试使用BV号作为oid。")
            return bv_number # 备用方案
    except requests.exceptions.RequestException as e:
        print(f"获取BV号 {bv_number} 的AID时发生网络错误: {e}。将尝试使用BV号作为oid。")
        return bv_number # 备用方案
    except json.JSONDecodeError:
         print(f"获取BV号 {bv_number} 的AID时解析响应发生JSON解码错误。将尝试使用BV号作为oid。")
         return bv_number # 备用方案
    except Exception as e:
         print(f"获取BV号 {bv_number} 的AID时发生未知错误: {e}。将尝试使用BV号作为oid。")
         return bv_number # 备用方案


# --- 如何使用 ---
if __name__ == "__main__":
    # 在这里列出你想要爬取的BV号
    bv_numbers_to_crawl = [
        # 选取5.12号b站综合热门视频前10
        "BV1MZFLeJEPR", #【春意红包2025】时隔八年的新老唱见合唱！祝大家巳巳如意，新春大吉！
        "BV1WXVoznEWv", # 电脑C盘爆红不用愁。教你4步彻底清理，安全不踩坑
        "BV1Z55VznEdq",  # 全程高能！历时60天，37位北大学生把106年前的历史写成游戏！破晓以后，重返五四！邀诸君躬身入局，亲手寻觅！
        "BV1odVtzREjb",  #毕设《父亲的早餐店》
        "BV1NhVZzsEdd",  #选 择 你 的 干 员 ！
        "BV1VRABehEzm",  #《丁 咔》
        "BV13bEMz3EBD",  #【2008.5.12-2025.5.12】今天，为汶川留一分钟
        "BV1vVELzeEpZ",  #天津早点吃法教程之方便面篇
        "BV1KFEMzcE5B",  #这玩意凭什么卖这么贵？！
        "BV1ui5PzLExa",  #一个人开发游戏，新增子弹击中水面水花特效音效，武器开火模式（视频后半段制作的后坐力蓝图，后面会大改下，集合到结构里取值，视频方法比较繁琐）
        "BV1Nf55zgEXP",  #独立游戏大电影！数年难遇【神作】！《Indie Cross》究竟讲了什么？
        "BV1Rs5LzHE2a",  #全球排名第一自助餐！每天500种美食！到底都吃什么？
        "BV126VrzVED4",  #「炉心融解」镜音リン【YYB式镜音铃】[4K/60FPS]
        "BV1pG5Mz7EeJ",  #三角洲行动 15万无后座100%命中率，真正的平民神器！全新暗杀流M4A1！【A】
        "BV1tf5NzEE7T",  #花7天蒸一个大馒头，切开以后惊呆了！
        "BV1VrVSz1Eme",  #【毕导】这个定律，预言了你的人生进度条
        "BV1GoVUz1Eow",  #角色触摸系统
        "BV1NLVSzYEhF",  #【白菜手书】第一次在中国买内衣就在大庭广众被量胸…太羞耻了啦！！💦
        "BV1zX5LzAEkc",  #帮我见证一下，她叫韩琳，欠我一份炒面！
        "BV1nXVRzkEYx",  #我叔十年前答应送我的直升飞机，造出来了
        "BV1g85Vz3E7t",  #大二下 周星驰《食神》仿拍
        "BV1wSEMzoEMk",  #今年暑假前，会有一款超级厉害的游戏问世
        "BV1Qs5VzCEGR",  #《河南游六花》
        "BV14kVRzJEgz",  #因为有你们，我每一步都走的那么坚定
        "BV1xE55zqEj8",  #探秘全球最大的国家！战斗民族，吃什么？
        "BV1YWE7zvE4t",  #花26万买翡翠赌石，一刀披麻布！
        "BV17q55zsEgd",  #游戏是逃离现实的通道，让我们成为每一段故事的主角！
        "BV1Va5MzeEXk",  #【原神】满命火神从蒙德城慢骑到纳塔话事处
        "BV1VFVQzHE9V",  #敌人看到指挥官第一视角直接吓哭了【三角洲行动】【蜂医日记】
        "BV151EuzEEQF",  #只是想看看她手机有没有下载反诈App



        # 可以添加更多BV号
    ]

    for bv in bv_numbers_to_crawl:
        crawl_data_and_append(bv)
        print("-" * 30) # 分隔不同BV号的爬取过程
        time.sleep(random.uniform(3, 15))