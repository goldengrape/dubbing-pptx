
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

# In[7]:


def short_tts(TEXT, xf_tts):
    Param, api, Lmax=xf_tts
    # 发送HTTP POST请求
    req = urllib.request.Request(
        api["url"], 
        data=construct_urlencode_utf8(TEXT), 
        headers=construct_header(api, construct_base64_str(Param)))
    response = urllib.request.urlopen(req)
    return response.read()


# 长句tts

# In[8]:


def long_tts(TEXT, xf_tts):
    Param, api, Lmax=xf_tts
    data=b''
    for sub_text in cut_string(TEXT, Lmax):
        data+=short_tts(sub_text, xf_tts)
    return data

def xf_save_tts(xf_tts, TEXT, filename):
    data=long_tts(TEXT, xf_tts)
    with open(filename, 'wb') as f:
        f.write(data)
    


# In[9]:


if __name__=="__main__":
    text='''
    刚才的分类是按白内障形成的原因来讲的, 比如老年性白内障, 外伤性白内障, 后发障之类. 

下面按白内障浑浊的位置来分类, 之所以这样分类, 是跟手术有关的, 

如果浑浊的区域是在晶状体中央的核, 那么称为核性白内障, 核性白内障一般中央的核比较硬, 医生会用一级到五级来形容核的硬度, 一级二级核都是很轻微的, 核也很小, 三级核会有些偏黄色,硬度根肥皂相似, 城市里大多数病人是在二级到三级核, 比这再硬的就是到四级核, 已经是深棕色, 不怎么透光了, 超声乳化手术做四级核就有点费力了, 而且核越硬, 核也越大, 皮质也越少, 手术风险就越高. 到五级核, 可能超声就不好用了, 需要用其他的手段把核摘出来, 五级核拿到体外看是个黑颗粒, 很硬, 扔到桌面上能反弹起来.

皮质性白内障是从周边开始浑浊的, 有点像冬天湖里结冰的样子, 楔形的, 一块一块的, 如果从外面一直遮挡到中央了, 病人的视力就变差了. 

后囊下白内障的位置是在晶状体后囊中央, 可能皮质与核都还是透明的, 只在后囊中心区域有一块类似锅巴的东西挡住. 但是后囊中心这个位置是眼球的后节点位置, 是一个特殊的位置, 光线很多是要经过这个点的, 这里被遮挡住对视力的影响很大. 

这几种类型的白内障症状是有不同的, 很有意思. 

核性白内障与后囊下白内障, 都是中央的区域被遮挡了, 周围还能透光. 所以这类的病人可能会说晚上的视力比白天好, 因为晚上瞳孔大, 周边透光多一些. 而皮质性白内障则相反, 很可能是白天视力好, 白天瞳孔小, 那些楔形的浑浊都被虹膜给遮挡住了,晚上的时候瞳孔大, 楔形浑浊暴露出来, 把光线胡乱散射, 视力就更差些. 



    '''
    xf_tts=init_xf_tts()
    print(xf_tts)
    xf_save_tts(xf_tts, text, "tts_test.mp3")

