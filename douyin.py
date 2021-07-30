# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 13:09:51 2021

@author: lbkj
"""

import requests
import json
from urllib import parse
import re
import csv

requests.adapters.DEFAULT_RETRIES = 5 # 增加重连次数
s = requests.session()
s.keep_alive = False # 关闭多余连接

save_path = "duba/"
# 抖音视频的URL : Request URL: 
request_url="https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=MS4wLjABAAAA7T7IYQgu_BSZ8Rg8ezVNuouU_njfub3d6lA_CxWwduk&max_cursor=1624191433000&count=10&publish_video_strategy_type=2&version_code=160100&version_name=16.1.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Mozilla&browser_version=5.0+(Windows+NT+10.0%3B+Win64%3B+x64)+AppleWebKit%2F537.36+(KHTML,+like+Gecko)+Chrome%2F91.0.4472.164+Safari%2F537.36&browser_online=true&_signature=_02B4Z6wo00101OWG35AAAIDBMkDy6CK47gzlhtsAAFho8d"
# 正则获取网页链接
base_url = "https://www.iesdouyin.com/aweme/v1/web/aweme/post/?"
sec_user_id_s = re.compile('sec_user_id=(.*?)&')
sec_user_id = re.search(sec_user_id_s, request_url).group(0)
max_cursor_s = re.compile('max_cursor=(.*?)&')
max_cursor = re.search(max_cursor_s, request_url).group(0)
signature_s = re.compile('(?<=browser_online=true&).*$')
signature = re.search(signature_s, request_url).group(0)
aid = "&aid=6383&"
url = base_url +sec_user_id + "&" +max_cursor + aid + signature

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    "referer":"https://www.douyin.com/",
}
# 调用requests中的get获取抖音作者主页的网页链接
r = requests.get(url=url, headers=headers, stream=True)
# print(r.text)

print("初始访问状态:", r)

# 使用json解析获取的网页内容
data_json = json.loads(r.text)
# print(data_json.keys())
has_more = data_json['has_more']
max_cursor = data_json['max_cursor']

# 判断hasmore是否为true，
# name需要根据max_cursor 这个字段来进行分页读取
# url上次返回的结果中的max_cursor 就是下一次url需要替换的分页数
while has_more == True:
    print('has_more:',has_more)
    url_parsed = parse.urlparse(url)#打散url连接
    bits = list(url_parsed) #将url连接区分开来
    qs = parse.parse_qs(bits[4]) #选择第四个元素
 
    qs['max_cursor'] = max_cursor #替换掉这个字段的值
    bits[4] = parse.urlencode(qs, True) #
    url_new = parse.urlunparse(bits) #

    # 只要hasmore是否为true，则反复访问作者主页链接，直到成功返回这个为false
    r = requests.get(url=url_new, headers=headers,stream=True)
    data_json = json.loads(r.text)
    has_more = data_json['has_more'] # 重置hasmore直到返回为false则退出循环
    max_cursor = data_json['max_cursor']# 每次重置这个页数，继续替换url中下一页页码进行访问
    # print('has_more22:',has_more)
    print('maxcursor22:', max_cursor)
    print('url_new:',url_new)
    print('has_more22:',len(data_json['aweme_list']))
    for i in range(len(data_json['aweme_list'])):   
        print(data_json['aweme_list'][i]['video']['play_addr_lowbr']['url_list'][0])

    path = "video"
    for i in range(len(data_json['aweme_list'])):
        # url_1为我们获取的视频链接
        url_1 = data_json['aweme_list'][i]['video']['play_addr_lowbr']['url_list'][0]
        # t为获取的视频标题
        t = data_json['aweme_list'][i]['desc']

        video_info = data_json['aweme_list'][i]["statistics"]
        # print(video_info)

        # requests发送浏览器发送get请求，得到数据
        r = requests.get(url=url_1, headers=headers,stream=True)
        print(r)    # 输出r访问状态
        # 获取数据的二进制长度
        reponse_body_lenth = int(r.headers.get("Content-Length"))
        # 打印数据的长度
        print("视频的数据长度为:", reponse_body_lenth)
        # *_path为完整文件保存路径
        video_path = t + '.mp4'
        info_path = t + '.json'
        csvinfo_path = t + '.csv'

        # 去除文件名中特殊字符
        rstr = r"[\/\\\:;\*#￥%$!@^……&()\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        # video_path = re.sub(rstr, "", video_path)  # 替换为""
        # csvinfo_path = re.sub(rstr, "", csvinfo_path)

        # # 保存点赞量等信息
        # with open(save_path + info_path, "wb") as f:
        #     f.write(json.dumps(video_info).encode('utf-8'))

        with open(save_path + csvinfo_path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, video_info.keys())
            w.writeheader()
        with open(save_path + csvinfo_path, "a", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, video_info.keys())
            writer.writerow(video_info)  # 按行写入数据
            # print("^_^ write success")

        # 保存抖音视频mp4格式，二进制读取
        with open(save_path + video_path, "wb") as xh:
            # 先定义初始进度为0
            write_all = 0
            for chunk in r.iter_content(chunk_size=100000000):
                write_all += xh.write(chunk)
                # 打印下载进度
                print("下载进度：%02.6f%%" % (100 * write_all / reponse_body_lenth))