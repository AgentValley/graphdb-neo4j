import os
import openai

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


def chat_with_open_ai(conversation, model="gpt-3.5-turbo-16k", temperature=0):
    messages = [{'role': x.get('role', 'assistant'),
                 'content': x.get('content', '')} for x in conversation]
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
            text = response['choices'][0]['message']['content']

            return text
        except Exception as oops:
            print(f'Error communicating with OpenAI: "{oops}"')

