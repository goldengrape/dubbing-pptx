
# coding: utf-8

# 重构google_speech
# 
# Forked from https://github.com/desbma/GoogleSpeech
# 
# 在如下几个方面进行改变:
# * 在中英文混合的语句中, 中文要读中文, 英文要读英文. 因为是调用了Google translate的非官方API, 所以Pubmed居然会被读成“帕布莫德”这样的可怕中文名. (已经完成)
# * 支持BytesIO的读写, (已经完成)
# * 并在内存内完成音频的拼接
# * 移除sox支持, 使之称为纯粹的python工具. 减少其他相关程序的安装. 受够了开源软件的一个又一个依赖. 

# In[1]:


""" Read a text using Google Translate TTS API. """

__version__ = "1.1.0"
__author__ = "goldengrape, fork from desbma https://github.com/desbma/GoogleSpeech"
__license__ = "LGPLv2"


# In[2]:


import argparse
import collections
import itertools
import logging
import os
import re
import subprocess
import string
import sys
import threading
import urllib.parse

import appdirs
import requests
import web_cache

from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play


# In[3]:


SUPPORTED_LANGUAGES = ("af", "ar", "bn", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "en-au", "en-ca", "en-gb",
                       "en-gh", "en-ie", "en-in", "en-ng", "en-nz", "en-ph", "en-tz", "en-uk", "en-us", "en-za", "eo",
                       "es", "es-es", "es-us", "et", "fi", "fr", "fr-ca", "fr-fr", "hi", "hr", "hu", "hy", "id", "is",
                       "it", "ja", "jw", "km", "ko", "la", "lv", "mk", "ml", "mr", "my", "ne", "nl", "no", "pl", "pt",
                       "pt-br", "pt-pt", "ro", "ru", "si", "sk", "sq", "sr", "su", "sv", "sw", "ta", "te", "th", "tl",
                       "tr", "uk", "vi", "zh-cn", "zh-tw")

PRELOADER_THREAD_COUNT = 1


# ```
# $ google_speech -o a.mp3 -l en 'hey'
# $ ffprobe -hide_banner a.mp3 
# Input #0, mp3, from 'a.mp3':
#   Duration: 00:00:00.77, start: 0.000000, bitrate: 32 kb/s
#     Stream #0:0: Audio: mp3, 24000 Hz, mono, fltp, 32 kb/s
# $ google_speech -o b.mp3 -l zh-cn '你好'
# $ ffprobe -hide_banner b.mp3 
# Input #0, mp3, from 'b.mp3':
#   Duration: 00:00:00.94, start: 0.000000, bitrate: 32 kb/s
#     Stream #0:0: Audio: mp3, 22050 Hz, mono, fltp, 32 kb/
# ```
# 对于google translate TTS返回的mp3， 居然中文和英文是两种不同的frame_rate，所以不能直接混合。

# In[4]:


class PreloaderThread(threading.Thread):

  """ Thread to pre load (download and store in cache) audio data of a segment. """

  def run(self):
    try:
        for segment in self.segments:
            acquired = segment.preload_mutex.acquire(blocking=False)
            if acquired:
                try:
                    if not segment.isInCache():
                        segment.preLoad()
                finally:
                    segment.preload_mutex.release()
    except Exception as e:
        logging.getLogger().error("%s: %s" % (e.__class__.__qualname__, e))


# 处理文本

# In[5]:


class Speech:

    """ Text to be read. """

    CLEAN_MULTIPLE_SPACES_REGEX = re.compile("\s{2,}")
    MAX_SEGMENT_SIZE = 100
    MIN_SEGMENT_SIZE = 50

    # 可能有中英文混排的文字, 所以应当设定两种语言. 如果是纯英文的, 两种语言就都设定成en好了. 
    def __init__(self, text, default_lang, switch_lang='en-us'): 
        self.text = self.cleanSpaces(text)+"."
        self.lang = default_lang
        self.default_lang=default_lang
        self.switch_lang=switch_lang
        
        self.cn_en_pattern, self.split_pattern=__class__.split_pattern()
        
    def __iter__(self):
        """ Get an iterator over speech segments. """
        return self.__next__()

    def __next__(self):
        """ Get a speech segment, 
        splitting text by taking into account spaces, 
        punctuation, and maximum segment size. """
        
        # 移除了--的部分
        segments = __class__.splitText(self, self.text)
        for segment_num, segment in enumerate(segments):
            if __class__.is_EN(segment):
                    now_lang=self.switch_lang
            else:
                    now_lang=self.default_lang
            yield SpeechSegment(segment, now_lang, segment_num, len(segments))

    def is_EN(text):
        c=text[0]
        return (c in string.ascii_letters)
                                       
    def split_pattern():
        cn_punc="！，。？、~@#￥%……&*（）：；《）《》“”()»〔〕-" #this line is Chinese punctuation
        en_punc=string.punctuation
        cn_en_pattern=re.compile(
            '[{}a-zA-Z ]+|[{}\u4e00-\u9fa50-9 {}]+'.format(en_punc,en_punc,cn_punc)
        )
        
        useless_chars = frozenset(
                              en_punc 
                              + string.whitespace
                              + cn_punc 
                              )
        split_pattern=re.compile("([\s\S]{"
                 +"{},{}".format(__class__.MIN_SEGMENT_SIZE, __class__.MAX_SEGMENT_SIZE)
                 + "}[useless_chars|(?!.\d+)|(?!,\d+)])")
        
        return cn_en_pattern, split_pattern

    
    def splitText(self,text):
        s=[]
        for t in self.cn_en_pattern.findall(text):
            if len(t)>__class__.MAX_SEGMENT_SIZE:
                s+=self.split_pattern.findall(t)
            else:
                s.append(t)
        return s
    

    @staticmethod
    def cleanSpaces(dirty_string):
        """ Remove consecutive spaces from a string. """
        return __class__.CLEAN_MULTIPLE_SPACES_REGEX.sub(" ",
                                                     dirty_string.replace("\n\n", "\n").replace("\t", " ").strip())

    def play(self, sox_effects=()):
        """ Play a speech. """

        # Build the segments
        preloader_threads = []
        segments = list(self)
        # start preloader thread(s)
        preloader_threads = [PreloaderThread(name="PreloaderThread-%u" % (i)) for i in range(PRELOADER_THREAD_COUNT)]
        for preloader_thread in preloader_threads:
            preloader_thread.segments = segments
            preloader_thread.start()


        # play segments
        for segment in segments:
            segment.play(sox_effects)


        # destroy preloader threads
        for preloader_thread in preloader_threads:
            preloader_thread.join()

    def save(self, path):
        """ Save audio data to an MP3 file. """
        with open(path, "wb") as f:
            self.savef(f)

    def savef(self, file):
        """ Write audio data into a file object. """
        combined = AudioSegment.empty()
        for segment in self:
            combined += segment.getAudioData()
        combined.export(file, 
                        format="mp3",
                        codec="libmp3lame")
    def test(self):
        combined = AudioSegment.empty()
        for segment in self:
            combined += segment.getAudioData()
        play(combined)         
#             segment.play( )
#         file.write(combined)


# 朗读

# In[6]:


class SpeechSegment:

    """ Text segment to be read. """

    BASE_URL = "https://translate.google.com/translate_tts"

    session = requests.Session()

    def __init__(self, text, lang, segment_num, segment_count=None):
        self.text = text
        self.lang = lang
        self.segment_num = segment_num
        self.segment_count = segment_count
        self.preload_mutex = threading.Lock()
        if not hasattr(__class__, "cache"):
            db_filepath = os.path.join(appdirs.user_cache_dir(appname="google_speech",
                                                            appauthor=False),
                                     "google_speech-cache.sqlite")
            os.makedirs(os.path.dirname(db_filepath), exist_ok=True)
            cache_name = "sound_data"
            __class__.cache = web_cache.ThreadedWebCache(db_filepath,
                                                       cache_name,
                                                       expiration=60 * 60 * 24 * 365,  # 1 year
                                                       caching_strategy=web_cache.CachingStrategy.LRU)
            logging.getLogger().debug("Total size of file '%s': %s" % (db_filepath,
                                                                     __class__.cache.getDatabaseFileSize()))
            purged_count = __class__.cache.purge()
            logging.getLogger().debug("%u obsolete entries have been removed from cache '%s'" % (purged_count, cache_name))
            row_count = len(__class__.cache)
            logging.getLogger().debug("Cache '%s' contains %u entries" % (cache_name, row_count))

    def __str__(self):
        return self.text

    def isInCache(self):
        """ Return True if audio data for this segment is present in cache, False otherwise. """
        url = self.buildUrl(cache_friendly=True)
        return url in __class__.cache

    def preLoad(self):
        """ Store audio data in cache for fast playback. """
        logging.getLogger().debug("Preloading segment '%s'" % (self))
        real_url = self.buildUrl()
        cache_url = self.buildUrl(cache_friendly=True)
        audio_data = self.download(real_url)
        assert(audio_data)
        __class__.cache[cache_url] = audio_data

    def getAudioData(self):
        """ Fetch the audio data. """
        with self.preload_mutex:
            cache_url = self.buildUrl(cache_friendly=True)
            if cache_url in __class__.cache:
                logging.getLogger().debug("Got data for URL '%s' from cache" % (cache_url))
                audio_data = __class__.cache[cache_url]
                assert(audio_data)
            else:
                real_url = self.buildUrl()
                audio_data = self.download(real_url)
                assert(audio_data)
                __class__.cache[cache_url] = audio_data
        return AudioSegment.from_mp3(BytesIO(audio_data))
        

    def play(self, sox_effects=()):
        """ Play the segment. """
        audio_data = self.getAudioData()
        logging.getLogger().info("Playing speech segment (%s): '%s'" % (self.lang, self))
        play(audio_data)
#         cmd = ["sox", "-q", "-t", "mp3", "-"]
#         if sys.platform.startswith("win32"):
#             cmd.extend(("-t", "waveaudio"))
#         cmd.extend(("-d", "trim", "0.1", "reverse", "trim", "0.07", "reverse"))  # "trim", "0.25", "-0.1"
#         cmd.extend(sox_effects)
#         logging.getLogger().debug("Start player process")
#         p = subprocess.Popen(cmd,
#                              stdin=subprocess.PIPE,
#                              stdout=subprocess.DEVNULL)
#         p.communicate(input=audio_data)
#         if p.returncode != 0:
#             raise RuntimeError()
#         logging.getLogger().debug("Done playing")
    
    def buildUrl(self, cache_friendly=False):
        """
        Construct the URL to get the sound from Goggle API.

        If cache_friendly is True, remove token from URL to use as a cache key.
        """
        params = collections.OrderedDict()
        params["client"] = "tw-ob"
        params["ie"] = "UTF-8"
        params["idx"] = str(self.segment_num)
        if self.segment_count is not None:
          params["total"] = str(self.segment_count)
        params["textlen"] = str(len(self.text))
        params["tl"] = self.lang
        lower_text = self.text.lower()
        params["q"] = lower_text
        return "%s?%s" % (__class__.BASE_URL, urllib.parse.urlencode(params))

    def download(self, url):
        """ Download a sound file. """
        logging.getLogger().debug("Downloading '%s'..." % (url))
        response = __class__.session.get(url,
                                         headers={"User-Agent": "Mozilla/5.0"},
                                         timeout=3.1)
        response.raise_for_status()
        return response.content

