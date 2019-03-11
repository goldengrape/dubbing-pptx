# dubbing-pptx

自动为PowerPoint幻灯片配音. 

提取每一页幻灯片中的备注, 使用语音合成(Text-To-Speech, TTS)产生配音, 并将配音音频插入到幻灯片中. 如果在PowerPoint/ Keyote中导出成视频, 可以产生自动配演讲解的视频. 

当前仅仅支持mac OS, Linux可能支持, 未测试. windows请先使用在线TTS

# 安装
先git clone吧

## 依赖
* [python-pptx](https://github.com/scanny/python-pptx)
* [GoogleSpeech](https://github.com/desbma/GoogleSpeech)
* [ffmpeg](https://formulae.brew.sh/formula/ffmpeg)

* 如在linux中, 应安装espeak
* 如使用讯飞TTS, 应先注册讯飞开放平台, 获得相应的key和ID, 并在讯飞填入自己的IP地址. 挺麻烦的, [参考这里](https://segmentfault.com/a/1190000013953185)
* 如使用google TTS
    * [sox](https://formulae.brew.sh/formula/sox) 这是个变声功能, 似乎我没用到这个功能, 但也还没找到方法去掉
    * 当使用google TTS时, 请自行准备“正常访问国际互联网”的工具. 

# 使用方法
* 使用本地TTS `python dubbing.py inputfile.pptx outputfile.pptx`
* 使用在线TTS
    * 讯飞TTS `python dubbing.py inputfile.pptx outputfile.pptx xunfei`
        * 当使用讯飞TTS时, 需要在API_setup.txt中写入您自己申请讯飞tts的key与ID
    * google TTS `python dubbing.py inputfile.pptx outputfile.pptx google`
        * 当使用google TTS时, 请自行准备“正常访问国际互联网”的工具. 
    
# Acknowledgement

This project is inspired by Sal Soghoian's great work [rendering presenter notes to audio.](https://iworkautomation.com/keynote/slide-presenter-notes.html)

# ToDo

* 参数表越来越混乱了, 需要修整一下
* sox似乎没必要安装啊, 看看能否跳过它.
* google tts读出来的好~慢~呐~, 保存语音的时候似乎没法调整速度, 看看能否用sox或者ffmpeg来调一下. 
