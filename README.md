# dubbing-pptx

自动为PowerPoint幻灯片配音. 

提取每一页幻灯片中的备注, 使用语音合成(Text-To-Speech, TTS)产生配音, 并将配音音频插入到幻灯片中. 如果在PowerPoint/ Keyote中导出成视频, 可以产生自动配演讲解的视频. 

当前仅仅支持mac OS, Linux可能支持, 未测试. windows请先使用在线TTS
# 安装
先git clone吧

## 依赖
* python-pptx
* ffmpeg
* 如在linux中, 应安装espeak
* 如使用讯飞TTS, 应先注册讯飞开放平台, 获得相应的key和ID, 并在讯飞填入自己的IP地址. 挺麻烦的, [参考这里](https://segmentfault.com/a/1190000013953185)

# 使用方法
* 使用本地TTS `python dubbing.py inputfile.pptx outputfile.pptx`
* 使用在线TTS(当前为讯飞) `python dubbing.py inputfile.pptx outputfile.pptx --online`
    * 当使用讯飞TTS时, 需要在API_setup.txt中写入您自己申请讯飞tts的key与ID
    
# Acknowledgement

This project is inspired by Sal Soghoian's great work [rendering presenter notes to audio.](https://iworkautomation.com/keynote/slide-presenter-notes.html)