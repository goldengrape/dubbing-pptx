
# coding: utf-8

# In[1]:


import re
import base64
import json
import time
import hashlib
import urllib.request
import urllib.parse
import json
import subprocess
import os


# ## 分割长字符串
# 
# 想用讯飞tts念长文章, webapi有长度限制, 所以要把一段字符串切分成多个, 切分时如果切断了英文单词或者中文词, 听起来就会很别扭. 所以, 将一个字符串分成若干子串, 子串的末尾以标点符号或者空格结尾(数字中小数点除外), 每个子串的长度是不超过L的最大值
# 
# 思路:
# 
# @gttnnn:
# 我当年在s60v2上因为类似的原因做了类似的事情，好像是txt大于10k还是多少讯飞那个app就打开超级慢。我是拿大文件整个读出来切出L那么一块，然后rfind找到最后一个句号。没有用正则是怕手机性能不够，没敢用😅
# 
# 所以:
# 写个generator, 从当前位置开始, 切除L个字, 然后在这段里找到最后一个标点位置, 把子串发出, 再把起始位置定在最后一个标点位置

# In[2]:


if __name__=="__main__":
    text="这一段话里面有数字2.34也有常规的英文标点. 但我不想把数字给切分开, ,,，,,, 应该怎么做呢?"


# In[3]:


def cut_string(text, Lmax):
    text+="\n"
    punc="([\s\S]{3," +str(Lmax)+ "}[,. ，。\n|(?!.\d+)|(?!,\d+)])"
    return iter(re.findall(punc,text))


# In[4]:


if __name__=="__main__":
    for sub_t in cut_string(text, 20):
        print(sub_t)
    


# # 讯飞tts

# 按照讯飞的要求, 分别配置设置的字符串, http请求的head和body

# In[5]:


def init_xf_tts():
    with open('API_setup.txt') as json_file:  
        api = json.load(json_file)
    # 构造输出音频配置参数
    Param = {
        "auf": "audio/L16;rate=16000",    #音频采样率
        "aue": "lame",    #音频编码，raw(生成wav)或lame(生成mp3)
        "voice_name": "aisjiuxu",
        "speed": "50",    #语速[0,100]
        "volume": "77",    #音量[0,100]
        "pitch": "30",    #音高[0,100]
        "engine_type": "aisound"    #引擎类型。aisound（普通效果），intp65（中文），intp65_en（英文）
    }
    Lmax=300
    xf_tts=(Param, api,Lmax)
    return xf_tts


# In[6]:


def construct_base64_str(Param):
    # 配置参数编码为base64字符串，过程：字典→明文字符串→utf8编码→base64(bytes)→base64字符串
    Param_str = json.dumps(Param)    #得到明文字符串
    Param_utf8 = Param_str.encode('utf8')    #得到utf8编码(bytes类型)
    Param_b64 = base64.b64encode(Param_utf8)    #得到base64编码(bytes类型)
    Param_b64str = Param_b64.decode('utf8')    #得到base64字符串
    return Param_b64str

def construct_header(api, Param_b64str):
    # 构造HTTP请求的头部
    time_now = str(int(time.time()))
    checksum = (api["key"] + time_now + Param_b64str).encode('utf8')
    checksum_md5 = hashlib.md5(checksum).hexdigest()
    header = {
        "X-Appid": api["id"],
        "X-CurTime": time_now,
        "X-Param": Param_b64str,
        "X-CheckSum": checksum_md5
    }
    return header

def construct_urlencode_utf8(t):
    # 构造HTTP请求Body
    body = {
        "text": t
    }
    body_urlencode = urllib.parse.urlencode(body)
    body_utf8 = body_urlencode.encode('utf8')
    return body_utf8


# 短句tts

# In[11]:


def short_tts(TEXT, xf_tts):
    Param, api, Lmax=xf_tts
    # 发送HTTP POST请求
    req = urllib.request.Request(
        api["url"], 
        data=construct_urlencode_utf8(TEXT), 
        headers=construct_header(api, construct_base64_str(Param)))
    response = urllib.request.urlopen(req)
    response_head = response.headers['Content-Type']
    if(response_head == "text/plain"):
        raise UserWarning("讯飞WebAPI错误: ", response.read().decode('utf8')["desc"])
#     return response.read()
    return response


# 长句tts

# In[8]:


def long_tts(TEXT, xf_tts):
    Param, api, Lmax=xf_tts
    data=[]
    for sub_text in cut_string(TEXT, Lmax):
        response = short_tts(sub_text, xf_tts)
        data.append(response.read())
#         data+=short_tts(sub_text, xf_tts)
    return data

def xf_save_tts(xf_tts, TEXT, filename):
    data=long_tts(TEXT, xf_tts)
    temp_filename_list=["tts_tmp_{}.mp3".format(index) for index in range(len(data))]
    
    for index, voice_piece in enumerate(data):
        temp_filename=temp_filename_list[index]
        with open(temp_filename, 'wb') as f:
            f.write(voice_piece)
    with open("temp_file_list.txt", "w") as f_temp:
        for temp_filename in temp_filename_list:
            f_temp.write("file '{}'\n".format(temp_filename))
    # concat with ffmpeg
#     ffmpeg -f concat -i mylist.txt -c copy output
    subprocess.run([
        "ffmpeg","-f","concat",
        "-i", "temp_file_list.txt",
        "-c", "copy",
        filename
    ])
    os.remove("temp_file_list.txt")
    for temp_filename in temp_filename_list:
        os.remove(temp_filename)


# In[12]:


if __name__=="__main__":
    text='''
只要晶状体出现浑浊，就叫白内障。
所以白内障实际上是一个很宽泛的概念。
我们知道人眼有2个透镜，1个是角膜，1个是晶状体, 相当于照相机上的镜头组，如果镜头之中有任何1个是混浊的，那么都会影响成像的质量。白内障可以是一部分的混浊，也可以是完全的混浊，
白内障患者的视觉有可能是部分影响，觉得看东西模糊, 也可能是完全就看不见了。如果双眼晶状体都完全浑浊不透光, 那么患者就是盲人了. 

白内障是全球第一位的致盲性眼病，但白内障导致的眼盲是可逆的，我们后面讲只要做白内障手术，就可以使白内障患者重见光明。

一个人, 如果眼睛看不到了，不但他自己失去工作和独立生活的能力，还需要有一个人来照顾她。这样就导致另一个人也无法继续工作. 
所以, 一个家庭可能会因为白内障致盲而从正常走向贫困。

但幸好白内障是可逆性的致盲性眼病，所以反过来说, 如果将白内障治好了, 那么她的家庭很可能因此而脱贫。

这就是为什么我们经常会听到有白内障扶贫手术这样的慈善活动. 
顺便说, 你是否知道全球不可逆的致盲性眼病，首要的原因是什么? 答案是青光眼。

    '''
    xf_tts=init_xf_tts()
    xf_save_tts(xf_tts, text, "tts_test.mp3")

