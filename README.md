# dubbing-pptx

自动为PowerPoint幻灯片配音. 

提取每一页幻灯片中的备注, 使用语音合成(Text-To-Speech, TTS)产生配音, 并将配音音频插入到幻灯片中. 如果在PowerPoint/ Keyote中导出成视频, 可以产生自动配演讲解的视频. 

当前仅仅支持mac OS
# 安装

## 依赖
* python-pptx


# 使用方法
`python dubbing.py inputfile.pptx outputfile.pptx`