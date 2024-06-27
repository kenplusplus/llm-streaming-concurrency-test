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

    def __init__(self, task_id:int, question:str, server:str, model:str, key:str) -> None:
        threading.Thread.__init__(self)
        self._start_time:float = None
        self._start_time_first_token:float = None
        self._response_time:float = None
        self._time_to_first_token:float = None
        self._question:str = question
        self._answer_complete:str = ""
        self._answer_chunks:list = []
        self._is_completed:bool = False
        self._task_id:int = task_id
        self._server:str = server
        self._model:str = model
        self._client = OpenAI(api_key=key, base_url=self._server)

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
    def task_id(self) -> int:
        return self._task_id

    def run(self) -> None:
        # record the time before the request is sent
        self._start_time = time.time()

        # send a ChatCompletion request to count to 100
        response = self._client.chat.completions.create(
            model=self._model,
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
        print(f"#{self.task_id:2d}-[{self.title:s}]: Total {self._response_time:3.2f} seconds, First Token Time: {self.time_to_first_token:3.2f} seconds, Throughput {len(self._answer_complete) / self._response_time:3.2f} chars/second")
        self._is_completed = True

def start():
    concurrent_number, question_file, server, model, key = parse_args()
    questions = load_questions(question_file)

    print("=========================================")
    print(f" Server     : {server:s}")
    print(f" Model      : {model}")
    print(f" Concurrent : {concurrent_number}")
    print(f" Question   : {question_file}")
    print("=========================================")

    total_questions = []

    if len(questions) < concurrent_number:
        for _ in range(int(concurrent_number / len(questions)) + 1):
            total_questions += questions
    else:
        total_questions = questions

    with Progress(
        TextColumn("[progress.description]{task.id}"),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn()
    ) as progress:
        infer_streams = []

        for index in range(concurrent_number):
            question = total_questions[index]
            task_id = progress.add_task(question, total=100)
            item = InferStreamThread(task_id, question, server, model, key)
            infer_streams.append(item)
            item.start()

        while not progress.finished:
            for item in infer_streams:
                answer_piece = item.answer_complete.replace('\n', ' ').replace('\r', '')
                answer_piece = answer_piece[-40:]
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
        print("  Throughput (chars/second): %f" % (total_throughput / len(infer_streams)))
        print("\n")

def parse_args():
    parser = argparse.ArgumentParser(description='LLM Concurrent Utility')
    parser.add_argument('-s','--server',
                        help='Server URL',
                        type=str,
                        default=LLM_SERVER_URL)
    parser.add_argument('-m','--model',
                        help='Model Name',
                        type=str,
                        default=LLM_MODEL_NAME)
    parser.add_argument('-k','--key',
                        help='API Key',
                        type=str,
                        default=LLM_API_KEY)
    parser.add_argument('-n','--concurrent-number',
                        help='Max Concurrent NUmber',
                        type=int,
                        default=MAX_CONCURRENT_NUM)
    parser.add_argument('-q','--question',
                        help='question file',
                        type=str,
                        default="questions.txt")
    args = vars(parser.parse_args())
    return (args["concurrent_number"], args['question'], args['server'], args['model'], args['key'])

if __name__ == "__main__":
    start()
