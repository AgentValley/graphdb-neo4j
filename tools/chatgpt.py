from time import sleep

import openai

from const import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS
from logger import log_info

openai.api_key = OPENAI_API_KEY


def get_relationships_among_concepts(concepts_dict):
    log_info('Found following concepts:', concepts_dict.keys())

    titles = concepts_dict.keys()
    concept_text = "\n\n".join([
        f"C{t}: {titles[t].get('concept', 'Empty')}\n"
        f"{t}: {titles[t].get('question', 'Empty')}\n"
        f"A{t}: {titles[t].get('answer', 'Empty')}"
        for t in range(1, len(titles) + 1)
    ])
    converstation = [
        {'role': 'system',
         'content': f'You are helpful tutor AI whose job is to embed text knowledge into graph database.'
                    f'The goal is to create concepts as nodes. Each concept have multiple questions and answers.'
                    f'Given a list of concepts, find relationships between them.'
                    f'Respond with these relationship in following format.'
                    f'C1--PREREQUISITE-->C2'
                    f'C3--SIMILARITY--0.8-->C4'
                    f'where C1, C2, C3... are the concepts, '
                    f'where Q1, Q2, Q3... are the questions in the concepts, '
                    f'the relation PREREQUISITE denotes that C1 has prerequisite C1'
                    f'0.8 in SIMILARITY represets the similarity factor between C3 and C4.'
                    f'The value of SIMILARITY ranges from 0.1 to 1.0 where 1.0 means they are the same in meaning.'},
        {'role': 'user', 'content': concept_text}
    ]

    relationship_str = chat_with_open_ai(conversation=converstation, temperature=1)
    return relationship_str


def chat_with_open_ai(conversation, model=OPENAI_MODEL, temperature=0):
    max_retry = 3
    retry = 0
    messages = [{'role': x.get('role', 'assistant'),
                 'content': x.get('content', '')} for x in conversation]
    while True:
        try:
            log_info('Calling OPENAI to find relationships')
            response = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)

            text = response['choices'][0]['message']['content']
            log_info('OPENAI Response Text', text)

            # trim message object
            debug_object = [i['content'] for i in messages]
            debug_object.append(text)
            if response['usage']['total_tokens'] >= OPENAI_MAX_TOKENS:
                messages = split_long_messages(messages)
                if len(messages) > 1:
                    messages.pop(1)

            return text
        except Exception as oops:
            print(f'Error communicating with OpenAI: "{oops}"')
            if 'maximum context length' in str(oops):
                messages = split_long_messages(messages)
                if len(messages) > 1:
                    messages.pop(1)
                print(' DEBUG: Trimming oldest message')
                continue
            retry += 1
            if retry >= max_retry:
                print(f"Exiting due to excessive errors in API: {oops}")
                return str(oops)
            print(f'Retrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)


def split_long_messages(messages):
    new_messages = []
    for message in messages:
        content = message['content']
        if len(content.split()) > 1000:
            # Split the content into chunks of 4096 tokens
            chunks = [content[i:i + 1000] for i in range(0, len(content), 1000)]

            # Create new messages for each chunk
            for i, chunk in enumerate(chunks):
                new_message = {'role': message['role'], 'content': chunk}
                if i == 0:
                    # Replace the original message with the first chunk
                    new_messages.append(new_message)
                else:
                    # Append subsequent chunks as new messages
                    new_messages.append({'role': message['role'], 'content': chunk})
        else:
            new_messages.append(message)  # No splitting required, add original message as it is

    return new_messages
