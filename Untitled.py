
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
speech.save("test.mp3")


# configuration: 
# --prefix=/usr/local/Cellar/ffmpeg/4.1.1-with-options 
# --enable-shared 
# --enable-hardcoded-tables 
# --cc=clang 
# --host-cflags= --host-ldflags= 
# --enable-gpl 
# --enable-libaom 
# --enable-libmp3lame --enable-libopus --enable-libsnappy --enable-libtheora --enable-libvorbis --enable-libvpx --enable-libx264 --enable-libx265 --enable-libfontconfig --enable-libfreetype --enable-frei0r --enable-libass --disable-libjack --disable-indev=jack --enable-opencl --enable-videotoolbox --disable-htmlpages --enable-libfdk-aac --enable-libopenh264 --enable-librsvg --enable-libsrt --enable-libvidstab --enable-libxvid --enable-nonfree
