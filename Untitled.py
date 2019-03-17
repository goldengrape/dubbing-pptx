
# coding: utf-8

# # from google_tts import Speech
# from io import BytesIO
# from pydub import AudioSegment
# 
# # say "Hello World"
# text = "Hello World, 你好世界!"
# lang = "zh-tw"
# speech = Speech(text, lang)
# # speech.play()
# 
# print(speech.splitText(text))
# 
# # you can also apply audio effects while playing (using SoX)
# # see http://sox.sourceforge.net/sox.html#EFFECTS for full effect documentation
# # sox_effects = ("speed", "1.5")
# # speech.play(sox_effects)
# 
# # save the speech to an MP3 file (no effect is applied)
# 
# 

# In[2]:


text='''
点开这篇Use of Orthokeratology for the Prevention of Myopic Progression in Children: A Report by the American Academy of Ophthalmology. 
你会看到一段摘要, 也就是abstract, 讲述了该文献的大致内容, 如果是临床试验研究, 往往读一下摘要就可以知道其研究结果, 如果嫌弃读英文烦, 也可以用上彩云小译的插件,

但对于大而全的综述, 最好找到全文, 去读读详细.

理论上, 文章的全文链接出现在右侧的Full text links, 但实际上往往点进去是要求付费的. 这是科学界自己也非常不爽的事情, 明明是拿着纳税人的钱做出的研究成果, 却无法分享给全社会, 而被科学杂志收取了费用, 甚至科学家自己不但没有稿费还经常要掏版面费.

'''


# In[3]:


speech = Speech(text, lang)
print(speech.splitText(text))
speech.save("error.mp3")


# In[5]:


from google_speech import Speech

# say "Hello World"
text = ["The atomic structure of the nucleosome has been revealed by X-ray crystallography,", 
        "delineating how this is important"]
lang = "en"
for t in text:
    speech = Speech(t,'en')
    speech.play()

# you can also apply audio effects while playing (using SoX)
# see http://sox.sourceforge.net/sox.html#EFFECTS for full effect documentation
# sox_effects = ("speed", "1.5")
# speech.play(sox_effects)

