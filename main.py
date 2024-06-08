import os
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

CURR_DIR=os.path.dirname(__file__)
LLM_SERVER_URL="http://101.201.111.141:8000/v1"
LLM_API_KEY="EMPTY"
MAX_CONCURRENT_NUM=5
LLM_MODEL_NAME="chatglm2-6b"

client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_SERVER_URL)

def load_questions():
    questions = []
    with open(os.path.join(CURR_DIR, "questions.txt"), "rt") as file:
        for line in file.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            questions.append(line)
    return questions
class InferStreamThread(threading.Thread):

    def __init__(self, task_id:int, question):
        threading.Thread.__init__(self)
        self._start_time = None
        self._start_time_first_token = None
        self._response_time = None
        self._time_to_first_token = None
        self._question = question
        self._answer_complete = ""
        self._answer_chunks = []
        self._is_completed = False
        self._task_id = task_id

    @property
    def is_completed(self):
        return self._is_completed

    @property
    def answer_complete(self) -> str:
        return self._answer_complete

    @property
    def response_time(self):
        return self._response_time

    @property
    def time_to_first_token(self):
        return self._start_time_first_token - self._start_time

    @property
    def task_id(self):
        return self._task_id

    def run(self):
        # record the time before the request is sent
        self._start_time = time.time()

        # send a ChatCompletion request to count to 100
        response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
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
                self._answer_complete += content
                self._answer_chunks.append([content,])

        # calculate the time it took to receive the response
        self._response_time = time.time() - self._start_time

        # print the time delay and text received
        print(f"[%s]: total {self._response_time:.2f} seconds, First Token Time: {self.time_to_first_token:.2f} seconds, Throughput {len(self._answer_complete) / self._response_time:.2f} tokens/second" % self._question)
        self._is_completed = True

def start():
    questions = load_questions()

    if len(questions) < MAX_CONCURRENT_NUM:
        print("ERROR: there are %d questions, not enough used for concurrent %d" % \
              (len(questions), MAX_CONCURRENT_NUM))

    with Progress(
        TextColumn("[progress.description]{task.id}"),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn()
    ) as progress:
        infer_streams = []

        for index in range(MAX_CONCURRENT_NUM):
            question = questions[index]
            task_id = progress.add_task(question, total=100)
            item = InferStreamThread(task_id, question)
            infer_streams.append(item)
            item.start()

        while not progress.finished:
            for item in infer_streams:
                answer_piece = item.answer_complete[-40:].\
                    replace('\n', ' ').replace('\r', '')
                progress.update(item.task_id, description=answer_piece)
                if item.is_completed:
                    progress.update(item.task_id, description=answer_piece + "[done]", completed=100)
            time.sleep(0.02)

        total_ttft = 0.0
        total_throughput = 0.0
        for item in infer_streams:
            total_ttft += item.time_to_first_token
            total_throughput += (len(item.answer_complete) / item.response_time)

        print("\n")
        print("Average [Concurrent: %d]" % MAX_CONCURRENT_NUM)
        print("=============================================== ")
        print("  First Token Time (seconds): %f" % (total_ttft / len(infer_streams)))
        print("  Throughput (tokens/second): %f" % (total_throughput / len(infer_streams)))
        print("\n")

if __name__ == "__main__":
    start()
