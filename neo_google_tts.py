
# coding: utf-8

# 重构google_speech
# 
# Forked from https://github.com/desbma/GoogleSpeech
# 
# 在如下几个方面进行改变:
# * 在中英文混合的语句中, 中文要读中文, 英文要读英文. 因为是调用了Google translate的非官方API, 所以Pubmed居然会被读成“帕布莫德”这样的可怕中文名. 
# * 支持BytesIO的读写, 并在内存内完成音频的拼接
# * 移除sox支持, 使之称为纯粹的python工具. 减少其他相关程序的安装. 受够了开源软件的一个又一个依赖. 

# In[251]:


from io import BytesIO
import re
from google_speech import Speech
from collections import Iterable


# In[258]:


class neoSpeech(Speech):
    def __init__(self, text, default_lang, switch_lang):
        self.text = self.cleanSpaces(text)
        self.lang = default_lang
        self.switch_lang=switch_lang
        self.switch_lang_pattern=__class__.split_cn_en_pattern()
        
    def __next__(self):
        """ Get a speech segment, splitting text by taking into account spaces, punctuation, and maximum segment size. """
        if self.text == "-":
            if sys.stdin.isatty():
                logging.getLogger().error("Stdin is not a pipe")
                return
            while True:
                new_line = sys.stdin.readline()
                if not new_line:
                    return
                segments = __class__.splitText(self, new_line)
                for segment_num, segment in enumerate(segments):
                    if __class__.is_EN(segment):
                        now_lang=self.switch_lang
                    else:
                        now_lang=self.lang
                    yield SpeechSegment(segment, now_lang, segment_num, len(segments))

        else:
            segments = __class__.splitText(self, self.text)
            for segment_num, segment in enumerate(segments):
                if __class__.is_EN(segment):
                        now_lang=self.switch_lang
                else:
                        now_lang=self.lang
                yield SpeechSegment(segment, now_lang, segment_num, len(segments))

    def is_EN(text):
        c=text[0]
        return ((c>='a' and c<="z") or (c>='A' and c<="Z"))
                                       
    def split_cn_en_pattern():
        punc='[{}]'.format(string.punctuation +"！，。？、~@#￥%……&*（）：；《）《》“”()»〔〕-")
        regex = []

        # Match a English string with space:
        regex += ["[a-zA-Z ]+"+punc+"*"]
        # Match a Chinese string:
        regex += ['[\u4e00-\ufaff0-9]+'+punc+"*"]
        regex = "|".join(regex)
        return re.compile(regex)

    
    def splitText(self,text):
        useless_chars = frozenset(
                              string.punctuation 
                              + string.whitespace
                              + "！，。？、~@#￥%……&*（）：；《）《》“”()»〔〕-" #this line is Chinese punctuation
                              )
        punc="([\s\S]{2," +str(__class__.MAX_SEGMENT_SIZE)+ "}[useless_chars|(?!.\d+)|(?!,\d+)])"
        
        s=[]
        for t in re.findall(punc,text):
            s += self.switch_lang_pattern.findall(t)                               
                                       
        return s

    def save(self, path):
        """ Save audio data to file or BytesIO. """
        if isinstance(path, str):
            with open(path, "wb") as f:
                for segment in self:
                    f.write(segment.getAudioData())
        
        if isinstance(path, BytesIO):
            for segment in self:
                path.write(segment.getAudioData())


# In[259]:


text= '''
iPad Pro    测试任务:
1. 单手持9iPad pro, 感觉重量.
2. 用iPad Pro原装键盘测试中文输入, 看速度和手指按错的错误率.
3. 用iPad pro原装的笔测试手写输入, 测试画图, 感觉笔尖在屏幕上滑动时摩擦力是否感觉舒适
4. 打开 https://www.photopea.com/  看能否在iPad pro的safari上流畅运行, 是否能够满足photoshop的大多数功能, 是否满足常用的照片编辑功能.
5. 找到安装有adobe lightroom的iPad pro, (问店员, 有些机器为了演示是预装好的). 看能否满足常用的照片编辑. 
6. 看这些app上的按钮大小是否可以舒适看清, 尽量使用手写笔进行操作, 评估操作舒适程度. 根据重量和操作舒适性选择屏幕的大小. 

'''


# In[260]:


# say "Hello World"
speech = neoSpeech(text, 'zh-cn','en')
speech.play()

# you can also apply audio effects while playing (using SoX)
# see http://sox.sourceforge.net/sox.html#EFFECTS for full effect documentation
sox_effects = ("speed", "1.5")
speech.play(sox_effects)

# save the speech to an MP3 file (no effect is applied)
f = BytesIO()
speech.save(f)


# In[225]:


def split_cn_en_pattern():
    punc='[{}]'.format(string.punctuation +"！，。？、~@#￥%……&*（）：；《）《》“”()»〔〕-")
    regex = []

    # Match a English string with space:
    regex += ["[a-zA-Z ]+"+punc+"*"]
    # Match a Chinese string:
    regex += ['[\u4e00-\ufaff0-9]+'+punc+"*"]
    regex = "|".join(regex)
    return re.compile(regex)

pattern=split_cn_en_pattern()

print(pattern.findall(text))


# In[238]:


def is_EN(text):
    c=text[0]
    return ((c>='a' and c<="z") or (c>='A' and c<="Z"))
print(is_EN('测试任务:'))


# In[221]:


is_EN('测试任务:')


# In[236]:


c='iPad Pro    '[0]
c='测试任务:'[0]
(c>='a' and c<="z") or ((c>='A' and c<="Z"))

