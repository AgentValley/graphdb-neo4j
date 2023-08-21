import openai

from const import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MODEL_LEGACY
from logger import log_error

openai.api_key = OPENAI_API_KEY


def chat_completion_with_open_ai(conversation, model=OPENAI_MODEL, temperature=0):
    messages = [{'role': x.get('role', 'assistant'),
                 'content': x.get('content', '')} for x in conversation]
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
            text = response['choices'][0]['message']['content']

            return text
        except Exception as oops:
            log_error(f'OpenAI Error:', oops)


def task_completion_with_open_ai(prompt, model=OPENAI_MODEL_LEGACY, temperature=0):
    while True:
        try:
            response = openai.Completion.create(model=model, prompt=prompt, temperature=temperature)
            text = response['choices'][0]['message']['content']

            return text
        except Exception as oops:
            log_error(f'OpenAI Error:', oops)
