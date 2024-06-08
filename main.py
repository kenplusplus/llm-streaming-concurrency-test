# imports
import time
import threading
from openai import OpenAI
import rich
from rich.console import Group
from rich.panel import Panel
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TaskProgressColumn
)
import os
client = OpenAI(api_key="EMPTY", base_url="http://101.201.111.141:8000/v1")

questions = [
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
    "请介绍下中国历史和主要人物",
    "请介绍下日本历史和主要人物",
    "请介绍下俄罗斯历史和主要人物",
    "请介绍下朝鲜历史和主要人物",
    "请介绍下美国历史和主要人物",
    "请介绍下印度历史和主要人物",
    "请介绍下蒙古历史和主要人物",
    "请介绍下英国历史和主要人物",
    "请介绍下加拿大历史和主要人物",
    "请介绍下澳大利亚历史和主要人物",
    "请介绍下新西兰历史和主要人物",
    "请介绍下芬兰历史和主要人物",
    "请介绍下德国历史和主要人物",
    "请介绍下希腊历史和主要人物",
    "请介绍下瑞典历史和主要人物",
]

class ChatThread(threading.Thread):

    def __init__(self, question=questions[0]):
        threading.Thread.__init__(self)
        self._start_time = None
        self._start_time_first_token = None
        self._response_time = None
        self._time_to_first_token = None
        self._question = question
        self._answer_all = ""
        self._answers = []

    def run(self):
        # record the time before the request is sent
        self._start_time = time.time()

        # send a ChatCompletion request to count to 100
        response = client.chat.completions.create(
            model='chatglm2-6b',
            messages=[
                {'role': 'user', 'content': self._question}
            ],
            temperature=1,
            stream=True
        )

        for chunk in response:
            if self._start_time_first_token == None:
                self._start_time_first_token = time.time()
            content = chunk.choices[0].delta.content
            if content is not None and len(content.strip()) != 0:
                self._answer_all += content
                self._answers.append([content,])

        # calculate the time it took to receive the response
        self._response_time = time.time() - self._start_time
        self._time_to_first_token = self._start_time_first_token - self._start_time

        # print the time delay and text received
        print(f"[%s]: total {self._response_time:.2f} seconds, First Token Time: {self._time_to_first_token:.2f} seconds, throughput {len(self._answer_all) / self._response_time:.2f} tokens/second" % self._question)

def start():
    chats = []
    for index in range(60):
        item = ChatThread(question=questions[index])
        chats.append(item)
        item.start()

    tasks = []

    with Progress(
        TextColumn("[progress.description]{task.id}"),
        TextColumn("[progress.description]{task.description}"),
        TaskProgressColumn(),
        TimeElapsedColumn()
    ) as progress:
        for item in chats:
            task = progress.add_task(item._question, total=10000)
            tasks.append(task)

        while not progress.finished:
            for index in range(len(tasks)):
                answer_piece = chats[index]._answer_all[-40:]
                answer_piece = answer_piece.replace('\n', ' ').replace('\r', '')
                progress.update(tasks[index], description=answer_piece, advance=0.1)
            time.sleep(0.02)
    for t in chats:
        t.join()


    """
    with Progress() as progress:

        task1 = progress.add_task("[red]Downloading...", total=1000)
        task2 = progress.add_task("[green]Processing...", total=1000)
        task3 = progress.add_task("[cyan]Cooking...", total=1000)

        while not progress.finished:
            progress.update(task1, advance=0.5)
            progress.update(task2, advance=0.3)
            progress.update(task3, advance=0.9)
            time.sleep(0.02)
    """

if __name__ == "__main__":
    start()