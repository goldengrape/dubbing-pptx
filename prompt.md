# 为ppt撰写演讲词

## 目的
读取一个ppt中的所有文本，依次为每一页撰写演讲词

## 过程设计
1. 读取pptx文件
2. 读取ppt中每一页的文字，包括正文中的文字和备注中的文字。
3. 对于第i页，令GPT依据全部文字和第i页的文字撰写演讲词
4. 将演讲词单独保存为markdown文件

## 函数设计
以Python撰写，以函数式编程的风格撰写结构化程序，最终以main()调用。

* 需要用的库
python-pptx, markdown

1. read_pptx(file_path: str) -> List[str]
作用描述：读取pptx文件并返回包含每一页的文本内容的列表
输入：文件路径（字符串）
输出：包含每一页文本内容的列表（字符串列表）

2. extract_text_and_notes(slide: pptx.slide.Slide) -> str
作用描述：从给定的PPT幻灯片中提取正文和备注中的文字
输入：幻灯片对象
输出：幻灯片中的文本内容（字符串）

3. generate_speech(slide_text: str, all_text: str, speech_duration: int, words_per_minute: int = 130) -> str
作用描述：根据给定的幻灯片文本和整个PPT的文本，以及用户输入的每一页期望的演讲时间，使用GPT生成相应字数的演讲词

输入：
    slide_text（字符串）：幻灯片文本
    all_text（字符串）：整个PPT的文本
    speech_duration（整数）：用户期望的单页演讲时间（单位：秒）
    words_per_minute（整数，可选）：默认每分钟的演讲字数（默认值：130）

输出：生成的演讲词（字符串）

4. save_to_markdown(speech_list: List[str], file_path: str) -> None
作用描述：将生成的演讲词列表保存为Markdown文件
输入：生成的演讲词列表（字符串列表），输出文件路径（字符串）
输出：无

5. main() -> None
作用描述：主函数，调用其他函数完成任务
输入：无
输出：无

## 细化函数

generate_speech()函数应当使用query_gpt3获取gpt的回复

```python
sleep_time=60 
def query_gpt3(prompt,cooldown_time=3):
    global sleep_time
    while True:
        try:
            # start_time=time.time()
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=[{
                "role": "user", 
                "content": prompt}]
                )
            # print(f"GPT-3 API time: {time.time()-start_time}")
            answer=response.choices[0].message.content.strip()
            time.sleep(cooldown_time)
            # print(f"after sleep 3s, I finished")
            sleep_time = int(sleep_time/2)
            sleep_time = max(sleep_time, 10)
            break
        except:
            print(f"API error, retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
            sleep_time += 10
            if sleep_time > 120:
                print("API error, aborting...")
                answer=""
                break
    # print(f"Answer: {answer}")
    return answer
```

所使用的prompt:
```python

prompt=f'''
请根据整个ppt的内容和当前页面的内容，产生当前页面的演讲词。
其中当前页面的内容为
【
{slide_text}
】
整个ppt的内容为
【
{all_text}
】
注意：
1. 演讲词大约{words_per_slide}字
2. 演讲词的语气应当{tone}
3. 演讲词的内容应当{content}

'''

```