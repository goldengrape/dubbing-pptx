
# coding: utf-8

# In[12]:


from google_tts import Speech as neo_Speech
from google_speech import Speech as ori_Speech
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play


text = "这一句话中既有中文又有" 
# This sentence has both Chinese and English.

lang = "zh-cn"
speech = ori_Speech(text,lang)
f = BytesIO()
speech.save("cn.mp3")
datacn = open('cn.mp3', 'rb').read()
f.write(datacn)
cn_voice = AudioSegment.from_mp3(BytesIO(datacn))
play(cn_voice)


# In[10]:


text = "This sentence has both Chinese and English" 
# This sentence has both Chinese and English.

lang = "en-us"
speech = ori_Speech(text,lang)
f = BytesIO()
speech.save("en.mp3")
dataen = open('en.mp3', 'rb').read()
f.write(dataen)
en_voice = AudioSegment.from_mp3(BytesIO(dataen))
play(en_voice)


# In[11]:


both=cn_voice+en_voice+cn_voice
play(both)

