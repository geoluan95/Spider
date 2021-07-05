# coding:utf-8
# __auth__ = "maiz"
# __date__ = "2021/6/27"

import json
import re,os
import requests
import ffmpeg.video
import subprocess

cookie = """_uuid=DAA18F27-6BFA-2E38-BC4C-F60C4AF0599081540infoc; buvid3=E6E47A83-F53F-44A1-82F2-AB97DF02A8FF34763infoc; CURRENT_FNVAL=80; blackside_state=1; rpdid=|(J|YJkmul|~0J'uYkJYJ~YJ); buvid_fp=E6E47A83-F53F-44A1-82F2-AB97DF02A8FF34763infoc; bsource=search_baidu; sid=hugiee8z; PVID=2; fingerprint=0acd05e7bcca97693925ee707a38da32; buvid_fp_plain=E6E47A83-F53F-44A1-82F2-AB97DF02A8FF34763infoc; DedeUserID=349902220; DedeUserID__ckMd5=3e8ad8f940acac21; SESSDATA=1f0328c2,1639207924,8d916*61; bili_jct=4f54db114f0e72caf3d13f5645ceecc4"""

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    "Referer": "https://www.bilibili.com/",  # 防盗链  告诉服务器你从哪里发送的请求
    "cookie": cookie
}


def get_response(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
    except:
        print(url + "请求失败")
        return None


def get_video_info(html_url):
    response = get_response(html_url)
    title = re.findall(r'<title data-vue-meta="true">(.*?)_哔哩哔哩_bilibili</title>', response.text)[0]
    html_data = re.findall(r'<script>window.__playinfo__=(.*?)</script>', response.text)[0]
    # print(html_data)
    # 将字符串转换成字典
    json_data = json.loads(html_data)
    # json字典根据键值对取值
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
    video_url = json_data['data']['dash']['video'][0]['baseUrl']
    video_info = [title, audio_url, video_url]
    return video_info


def save(title, audio_url, video_url):
    # 保存视频、音频 图片 都是二进制数据
    audio_url_content = get_response(audio_url).content
    video_url_content = get_response(video_url).content
    with open(title+".mp3", "wb") as f:
        f.write(audio_url_content)
    with open(title+".mp4", "wb") as f_1:
        f_1.write(video_url_content)
    print(title+"视频内容保存完成")
 

def video_add_mp3(file_name,mp3_file,outfile_name):
    cmd = 'D:/ffmpeg/bin/ffmpeg -i ' + file_name + ' -i ' + mp3_file + ' -acodec copy ' + outfile_name
    print(cmd)
    subprocess.call(cmd, shell=True)
    os.remove(file_name)
    os.remove(mp3_file)
    print('Done')

if __name__ == '__main__':
    """
    for i in range(1,2):
        html_url = "https://www.bilibili.com/video/BV1hk4y197Df/?spm_id_from=333.788.recommend_more_video.-{}".format(i)
        print(html_url)
        video_info = get_video_info(html_url)
        save(video_info[0], video_info[1], video_info[2],i)
        file_name = str(i)+video_info[0] + '.mp4'
        print(file_name)
        mp3_file = str(i) + video_info[0] + '.mp3'
        outfile_name = str(i) + video_info[0] + '_out.mp4'
        video_add_mp3(file_name, mp3_file, outfile_name)
    """
    html_url = "https://www.bilibili.com/video/BV1WK4y1J74k?from=search&seid=12416113293449637734"
    print(html_url)
    video_info = get_video_info(html_url)
    save(video_info[0], video_info[1], video_info[2])
    file_name =  video_info[0] + '.mp4'
    print(file_name)
    mp3_file = video_info[0] + '.mp3'
    outfile_name = video_info[0] + '_out.mp4'
    video_add_mp3(file_name, mp3_file, outfile_name)
    