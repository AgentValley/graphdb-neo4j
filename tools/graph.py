import re

from graphdb.client import Neo4jClient
from logger import log_info, log_warn
from tools.chatgpt import task_completion_with_open_ai


def create_concept_text(concepts_dict=None, concepts_list=None):
    concept_text = None
    if concepts_dict:
        concepts = concepts_dict.keys()
        concept_text = "\n\n".join([
            f"{concepts[t].get('concept_id')}: {concepts[t].get('topic', 'Empty')}\n"
            f"Q[{concepts[t].get('concept_id')}]: {concepts[t].get('question', 'Empty')}\n"
            f"W[{concepts[t].get('concept_id')}]: {concepts[t].get('weightage')}" if concepts[t].get(
                'weightage') else ""
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

    prompt = f'You are helpful tutor AI whose job is to embed text knowledge into graph database. ' \
             f'The goal is to create concepts as nodes. Each concept have multiple questions and answers. ' \
             f'Given a list of concepts, find relationships between them. ' \
             f'Respond with these relationship in following format. \n' \
             f'C1--PREREQUISITE_OF-->C2 \n' \
             f'C3--SIMILARITY--0.8-->C4 \n' \
             f'where C1, C2, C3... are the concepts, \n' \
             f'where Q[1], Q[2], Q[3]... are the questions in the concepts, \n' \
             f'where W[1], W[2], W[3]... are the weightage of concepts, \n' \
             f'the relation PREREQUISITE_OF denotes that C1 has prerequisite C1 \n' \
             f'0.8 in SIMILARITY represets the similarity factor between C3 and C4. \n' \
             f'The value of SIMILARITY ranges from 0.1 to 1.0 where 1.0 means they are the same in meaning.' \
             'Generate for the following concepts:\n' \
             f'{concept_text}'

    # converstation = [{'role': 'system', 'content': prompt}]
    relationship_str = task_completion_with_open_ai(prompt)
    return relationship_str


def find_prerequisite_relationship_of_concept(concept, existing_concepts):
    existing_concepts_text = create_concept_text(concepts_list=existing_concepts)
    if not existing_concepts_text:
        return ""

    prompt = f'You are an AI tutor whose job is to embed text knowledge into graph database. ' \
             f'Given a list of concepts: \n' \
             f'{existing_concepts_text}' \
             f'where C1, C2, C3... are the names of the concept, \n' \
             f'where Q[1], Q[2], Q[3]... are the questions in the concepts, \n' \
             f'Respond only with the prerequisite relationship of given concept by user wh other conceptsit. ' \
             f'For example, \n' \
             f'C1--PREREQUISITE_OF-->C2 \n' \
             f'C2--PREREQUISITE_OF-->C3 \n' \
             f'where PREREQUISITE_OF denotes that C1 is prerequisite of C2 and C2 is prerequisite of C3.' \
             'Generate relationship for the following concept:' \
             f'{concept.get("concept_id")}: {concept.get("topic")}\n' \
             f'Q[{concept.get("concept_id")}]: {concept.get("question")}'

    # converstation = [{'role': 'system', 'content': prompt}, ]

    relationship_str = task_completion_with_open_ai(prompt)
    return relationship_str


def find_weightage_of_concepts(concept, existing_concepts):
    existing_concepts_text = create_concept_text(concepts_list=existing_concepts)

    prompt = f'You are helpful tutor AI whose job is to embed text knowledge into graph database. ' \
             f'Given a list of concepts: \n' \
             f'{existing_concepts_text}' \
             f'where C1, C2, C3... are the concepts, ' \
             f'where Q[1], Q[2], Q[3]... are the questions in the concepts, ' \
             f'where W[1], W[2], W[3]... are the weightage of concepts, ' \
             f'Respond only with the weightage of given concept, for example. \n' \
             f'C1--0.8 \n' \
             f'where 0.8 denotes the weightage of C1 among all other concepts' \
             'Generate weightage for this concept:' \
             f'{concept.get("concept_id")}: {concept.get("topic")}\n' \
             f'Q[{concept.get("concept_id")}]: {concept.get("question")}'

    # converstation = [{'role': 'system', 'content': prompt}]
    weightage_str = task_completion_with_open_ai(prompt)

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


def parse_relationships_string_with_regex(relationships_string):
    prerequisites = {}
    similarities = {}

    relationship_pattern = r'(\S+)--(PREREQUISITE|SIMILARITY)(--(?:\S+|\d+\.\d+))?-->(\S+)'
    matches = re.findall(relationship_pattern, relationships_string, re.MULTILINE)

    for match in matches:
        source_node, relationship_type, value, target_node = match
        target_node = target_node.strip()

        if target_node != source_node:
            if relationship_type == "PREREQUISITE":
                if target_node not in prerequisites:
                    prerequisites[target_node] = [source_node]
                else:
                    prerequisites[target_node].append(source_node)
            elif relationship_type == "SIMILARITY":
                similarity_value = float(value.split('--')[1])
                if target_node not in similarities:
                    similarities[target_node] = {source_node: similarity_value}
                else:
                    similarities[target_node][source_node] = similarity_value

    return prerequisites, similarities


def parse_prerequisite_relationships_string_with_regex(relationships_string, concept=None):
    prerequisites = {}

    relationship_pattern = r'(\S+)--PREREQUISITE_OF-->(\S+)'
    matches = re.findall(relationship_pattern, relationships_string, re.MULTILINE)

    given_concept_id = concept.get('concept_id') if concept else None
    for match in matches:
        source_node, target_node = match
        target_node = target_node.strip()

        if given_concept_id and given_concept_id not in target_node and given_concept_id not in source_node:
            continue

        if target_node != source_node:
            if target_node not in prerequisites:
                prerequisites[target_node] = [source_node]
            else:
                prerequisites[target_node].append(source_node)

    return prerequisites


def create_nodes(uid, cid, concepts_dict=None, concepts_list=None):
    client = Neo4jClient()

    teacher = client.get_teacher(uid)
    if not teacher:
        log_info('Teacher does not exists, creating Teacher')
        teacher = client.create_teacher(uid)
    log_info('Teacher', teacher)

    course = client.get_course(cid)
    if not course:
        log_info('Course does not exists, creating Course')
        course = client.create_course_for_teacher(cid, uid)
    log_info('Course', course)

    # Add concepts by dictionary
    if concepts_dict:
        topics = concepts_dict.keys()
        for topic in topics:
            params = topics[topic]
            params['course_id'] = cid
            client.create_concept(params)

    # Add concepts by list
    if concepts_list:
        for concept in concepts_list:
            if concept:
                params = concept
                params['course_id'] = cid
                client.create_concept(params)


def create_prerequisite_relationship(qid, prerequisites):
    client = Neo4jClient()

    if prerequisites and isinstance(prerequisites, list):
        for pid in prerequisites:
            client.create_prerequisite_relationship(qid, pid)

    if prerequisites and isinstance(prerequisites, dict):
        for _qid in prerequisites.keys():
            prerequisites_for_qid = prerequisites[_qid]
            for pid in prerequisites_for_qid:
                client.create_prerequisite_relationship(_qid, pid)


def create_similarity_relationship(similarities):
    client = Neo4jClient()
    if similarities and similarities is not {}:
        for qid in similarities.keys():
            similarities_for_qid = similarities[qid]
            for sid in similarities_for_qid.keys():
                if similarities_for_qid.get(sid) is not None:
                    client.create_similarity_relationship(qid, sid, similarities_for_qid.get(sid))


def delete_concept_node_and_relationship(concept_id):
    if concept_id:
        client = Neo4jClient()
        client.delete_concept(concept_id)
        client.delete_relationship_of_concept(concept_id)


if __name__ == "__main__":
    s = '22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->a0b94d13-1f0f-458e-8f34-3ddcef83c33f\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->cc24ee53-00f8-462a-b306-97d1204b50c1\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->d7a3d7aa-e4fb-42e6-9752-286ba4256cf6\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->a19689159-1b90-43e0-b640-6a22bc0f5ab6'
    result = parse_relationships_string_with_regex(s)
    print(result)
