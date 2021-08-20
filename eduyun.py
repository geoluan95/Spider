# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 18:57:01 2021

@author: luan
"""

# -*- coding: utf-8 -*-
import requests
import os, re
import subprocess
import urllib
from lxml import html
from bs4 import BeautifulSoup
#url = "https://hknm5s6gzvm5a6wju24.exp.bcevod.com/mda-kbbw3kjrstzesazt/mda-kbbw3kjrstzesazt.m3u8"

html_url = "https://ykt.eduyun.cn/ykt/jtjj/zhuan6.html"

def get_htmlurl(html,headers):
    response = requests.get(html, headers).content.decode('utf-8')
    #response = etree.HTML(response)
    soup = BeautifulSoup(response,'lxml')
    htmlurl=[]
    for i, temp in enumerate(soup.find_all("dt")):
        # print(temp.a['href'])
        htmlurl.append("https://ykt.eduyun.cn/ykt/jtjj/"+temp.a['href'])
         
    return htmlurl
          
def get_videourl(html_url_list):
    m3u8_url_list = []
    title = []
    for i, html_url in enumerate(html_url_list):
        response = requests.get(html_url, headers).content.decode('utf-8')
        soup = BeautifulSoup(response,'lxml')
        
        title.append(soup.h3.string)
        
        for item in soup.find_all("script")[1]:
            #item = str(item)
            r = re.findall('https?://(?:.*m3u8)',item)[0]
        m3u8_url_list.append(r)
    
    return m3u8_url_list, title
            
            
def ts2mp4(filepath, filename):
    cmd = 'copy /b *.ts {}'.format(filename)
    subprocess.call(cmd, shell=True)
try:
    headers = {
        #"Cookie":"  ",   # 更换自己的Cookie 
        "Referer":"https://ykt.eduyun.cn/ykt/yktparentchildc/20200221/33718.html",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    }
    
    html_url_list = get_htmlurl(html_url, headers)
    m3u8_list, title = get_videourl(html_url_list)
    
    for i, url in enumerate(m3u8_list):
        req = requests.get(url, headers=headers)
        req.raise_for_status()
        req.encoding = req.apparent_encoding
        # print("req.text:", req.text)
        vi = url.strip().split('/')[3]
        content = req.text.split("\n")
        for line in content:
            print(line)
            if len(line)>0 and line[:1]!= "#":
                url = "https://hknm5s6gzvm5a6wju24.exp.bcevod.com/{}/{}".format(vi,line)
                r = requests.get(url, headers=headers)
                req.raise_for_status()
                filename = line
                save_path = "{}/".format(title[i])
                if not os.path.exists(save_path):
                    os.mkdir(save_path)
                with open(save_path + filename,"wb") as f:
                    f.write(r.content) 
    
except Exception as e:
    print(e)
