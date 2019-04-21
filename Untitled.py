
# coding: utf-8

# In[1]:


text='''高阶像差的一个最主要的例子是球差，也就是球面像差。关于球面像差我还是建议你们去试一下那个实验图，大家可以用一个小的软件就可以亲身体会到，球面镜是怎么样去折射光线。并且你会发现随着你移动入射光线，其实根本就没有办法聚焦到同一个点上。

球差，之所以比较重要，是因为人眼换上球面镜的人工晶体了以后，会把人眼的球面像差增大一些。

本来角膜是一个正球差的透镜，天然晶状体是一个负球差的透镜，他们两个互相之间会抵消一部分，人眼的总球差很小。但是当换上了人工晶体了以后呢，早期人工晶体本身是球面的，它一定是一个正球差，于是虽然可以把低阶的近视远视矫正得很好，却引入了新的高阶的球差。


'''


# In[2]:


from xunfei_tts import Speech as xf_Speech
import json
with open('API_setup.txt') as json_file:  
            api = json.load(json_file)
            ve = xf_Speech(api, voice_name="x_yifeng")
            
ve.play(text)
ve.save(text,"test.mp3")


# In[3]:


ve.splitText(text)

