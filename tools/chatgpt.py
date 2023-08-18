import re
from time import sleep

import openai

from const import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS
from logger import log_info, log_warn

openai.api_key = OPENAI_API_KEY


def create_concept_text(concepts_dict=None, concepts_list=None):
    concept_text = None
    if concepts_dict:
        concepts = concepts_dict.keys()
        concept_text = "\n\n".join([
            f"{concepts[t].get('concept_id')}: {concepts[t].get('topic', 'Empty')}\n"
            f"Q[{concepts[t].get('concept_id')}]: {concepts[t].get('question', 'Empty')}\n"
            f"W[{concepts[t].get('concept_id')}]: {concepts[t].get('weightage')}" if concepts[t].get('weightage') else ""
            for t in range(0, len(concepts))
        ])

    if concepts_list:
        concept_text = "\n\n".join([
            f"{concept.get('concept_id')}: {concept.get('topic', 'Empty')}\n"
            f"Q[{concept.get('concept_id')}]: {concept.get('question', 'Empty')}\n"
            f"W[{concept.get('concept_id')}]: {concept.get('weightage', 0.5)}" if concept.get('weightage') else ""
            for concept in concepts_list if concept
        ])

    return concept_text


def get_relationships_among_concepts(concepts_dict=None, concepts_list=None):
    concept_text = create_concept_text(concepts_dict=concepts_dict, concepts_list=concepts_list)
    if not concept_text:
        return ""

    converstation = [
        {'role': 'system',
         'content': f'You are helpful tutor AI whose job is to embed text knowledge into graph database. '
                    f'The goal is to create concepts as nodes. Each concept have multiple questions and answers. '
                    f'Given a list of concepts, find relationships between them. '
                    f'Respond with these relationship in following format. \n'
                    f'C1--PREREQUISITE_OF-->C2 \n'
                    f'C3--SIMILARITY--0.8-->C4 \n'
                    f'where C1, C2, C3... are the concepts, \n'
                    f'where Q[1], Q[2], Q[3]... are the questions in the concepts, \n'
                    f'where W[1], W[2], W[3]... are the weightage of concepts, \n'
                    f'the relation PREREQUISITE_OF denotes that C1 has prerequisite C1 \n'
                    f'0.8 in SIMILARITY represets the similarity factor between C3 and C4. \n'
                    f'The value of SIMILARITY ranges from 0.1 to 1.0 where 1.0 means they are the same in meaning.'},
        {'role': 'user', 'content': concept_text}
    ]

    relationship_str = chat_with_open_ai(conversation=converstation, temperature=1)
    return relationship_str


def find_prerequisite_relationship_of_concept(concept, existing_concepts):
    existing_concepts_text = create_concept_text(concepts_list=existing_concepts)
    if not existing_concepts_text:
        return ""

    converstation = [
        {'role': 'system',
         'content': f'You are helpful tutor AI whose job is to embed text knowledge into graph database. '
                    f'Given a list of concepts: \n'
                    f'{existing_concepts_text}'
                    f'where C1, C2, C3... are the names of the concept, \n'
                    f'where Q[1], Q[2], Q[3]... are the questions in the concepts, \n'
                    f'Respond only with the prerequisite relationship of given concept by user wh other conceptsit. '
                    f'For example, \n'
                    f'C1--PREREQUISITE_OF-->C2 \n'
                    f'C2--PREREQUISITE_OF-->C3 \n'
                    f'where PREREQUISITE_OF denotes that C1 is prerequisite of C2 and C2 is prerequisite of C3.'},
        {'role': 'user', 'content': f'{concept.get("concept_id")}: {concept.get("topic")}\n'
                                    f'Q[{concept.get("concept_id")}]: {concept.get("question")}'}
    ]

    relationship_str = chat_with_open_ai(conversation=converstation, temperature=1)
    return relationship_str


def find_weightage_of_concepts(concept, existing_concepts):
    existing_concepts_text = create_concept_text(concepts_list=existing_concepts)

    converstation = [
        {'role': 'system',
         'content': f'You are helpful tutor AI whose job is to embed text knowledge into graph database. '
                    f'Given a list of concepts: \n'
                    f'{existing_concepts_text}'
                    f'where C1, C2, C3... are the concepts, '
                    f'where Q[1], Q[2], Q[3]... are the questions in the concepts, '
                    f'where W[1], W[2], W[3]... are the weightage of concepts, '
                    f'Respond only with the weightage of given concept, for example. \n'
                    f'C1--0.8 \n'
                    f'where 0.8 denotes the weightage of C1 among all other concepts'},
        {'role': 'user', 'content': f'{concept.get("concept_id")}: {concept.get("topic")}\n'
                                    f'Q[{concept.get("concept_id")}]: {concept.get("question")}'}
    ]

    weightage_str = chat_with_open_ai(conversation=converstation, temperature=1)
    pattern = r'(\S+)--(\d+\.\d+)'
    matches = re.findall(pattern, weightage_str, re.MULTILINE)
    for match in matches:
        concept_id, weightage = match
        if concept.get("concept_id") in concept_id:
            try:
                return float(weightage)
            except Exception as e:
                log_warn(f'Failed to get weightage of {concept.get("concept_id")}: {e}')

    return 0.5


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
            print(f'Retrying in {2 ** (retry - 1) * 3} seconds...')
            sleep(2 ** (retry - 1) * 3)


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
