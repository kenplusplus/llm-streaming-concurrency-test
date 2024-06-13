import os
import time
import threading
import argparse
from openai import OpenAI
from rich.console import Group
from rich.panel import Panel
from rich.live import Live
from rich.progress import (
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

CURR_DIR=os.path.dirname(__file__)
LLM_SERVER_URL="http://101.201.111.141:8000/v1"
LLM_API_KEY="EMPTY"
MAX_CONCURRENT_NUM=5
LLM_MODEL_NAME="chatglm2-6b"

client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_SERVER_URL)

def load_questions(question_file) -> list:
    questions = []
    with open(os.path.join(CURR_DIR, question_file), "rt") as file:
        for line in file.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            questions.append(line)
    return questions

class InferStreamThread(threading.Thread):

    def __init__(self, task_id:int, question:str) -> None:
        threading.Thread.__init__(self)
        self._start_time:float = None
        self._start_time_first_token:float = None
        self._response_time:float = None
        self._time_to_first_token:float = None
        self._question:str = question
        self._answer_complete:str = ""
        self._answer_chunks:list = []
        self._is_completed:bool = False
        self._task_id = task_id

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    @property
    def title(self) -> str:
        if len(self._question) > 20:
            return self._question[:20] + "..."
        return self._question

    @property
    def answer_complete(self) -> str:
        return self._answer_complete

    @property
    def response_time(self) -> float:
        return self._response_time

    @property
    def time_to_first_token(self) -> float:
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
        print(f"#{self.task_id:2d}-[{self.title:s}]: Total {self._response_time:3.2f} seconds, First Token Time: {self.time_to_first_token:3.2f} seconds, Throughput {len(self._answer_complete) / self._response_time:3.2f} tokens/second")
        self._is_completed = True

def start():
    concurrent_number, question_file = parse_args()
    questions = load_questions(question_file)

    if len(questions) < concurrent_number:
        print("ERROR: there are %d questions, not enough used for concurrent %d" % \
              (len(questions), concurrent_number))
        exit(1)

    with Progress(
        TextColumn("[progress.description]{task.id}"),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn()
    ) as progress:
        infer_streams = []

        for index in range(concurrent_number):
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
        print("Average [Concurrent: %d]" % concurrent_number)
        print("=============================================== ")
        print("  First Token Time (seconds): %f" % (total_ttft / len(infer_streams)))
        print("  Throughput (tokens/second): %f" % (total_throughput / len(infer_streams)))
        print("\n")

def parse_args():
    parser = argparse.ArgumentParser(description='LLM Concurrent Utility')
    parser.add_argument('-n','--concurrent-number',
                        help='Max Concurrent NUmber',
                        type=int,
                        default=MAX_CONCURRENT_NUM)
    parser.add_argument('-q','--question',
                        help='question file',
                        type=str,
                        default="questions.txt")
    args = vars(parser.parse_args())
    return (args["concurrent_number"], args['question'])

if __name__ == "__main__":
    start()
