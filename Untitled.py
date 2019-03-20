
# coding: utf-8

# In[1]:


from google_tts import Speech as neo_Speech
from google_speech import Speech as ori_Speech
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play


text = "这一句话This sentence中既有中文又有English，" 
# This sentence has both Chinese and English.

lang = "zh-cn"
speech = neo_Speech(text,lang)


# In[2]:


text = "This sentence has both Chinese and English" 
# This sentence has both Chinese and English.

lang = "en-us"
speech = ori_Speech(text,lang)
f = BytesIO()
speech.save("en.mp3")
dataen = open('en.mp3', 'rb').read()
f.write(dataen)
en_voice = AudioSegment.from_mp3(BytesIO(dataen))
# play(en_voice)


# In[5]:


combined = AudioSegment.empty()
combined += cn_voice
combined += en_voice
play(combined)

