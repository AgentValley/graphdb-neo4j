import re

from graphdb.client import Neo4jClient
from logger import log_info


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


def create_prerequisite_relationship(prerequisites):
    client = Neo4jClient()
    if prerequisites and prerequisites is not {}:
        for qid in prerequisites.keys():
            prerequisites_for_qid = prerequisites[qid]
            for pid in prerequisites_for_qid:
                client.create_prerequisite_relationship(qid, pid)


def create_similarity_relationship(similarities):
    client = Neo4jClient()
    if similarities and similarities is not {}:
        for qid in similarities.keys():
            similarities_for_qid = similarities[qid]
            for sid in similarities_for_qid.keys():
                if similarities_for_qid.get(sid) is not None:
                    client.create_similarity_relationship(qid, sid, similarities_for_qid.get(sid))


if __name__ == "__main__":
    s = '22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->a0b94d13-1f0f-458e-8f34-3ddcef83c33f\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->cc24ee53-00f8-462a-b306-97d1204b50c1\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->d7a3d7aa-e4fb-42e6-9752-286ba4256cf6\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->a19689159-1b90-43e0-b640-6a22bc0f5ab6'
    result = parse_relationships_string_with_regex(s)
    print(result)
