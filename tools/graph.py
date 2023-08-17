import re

from graphdb.client import Neo4jClient
from logger import log_info


def parse_relationships_string_with_regex(relationships_string):
    prerequisites = {}
    similarities = {}

    relationship_pattern = r'(\S+)--(PREREQUISITE|SIMILARITY)(--(?:\S+|\d+\.\d+))?-->(\S+)'
    matches = re.findall(relationship_pattern, relationships_string)

    for match in matches:
        source_node, relationship_type, value, target_node = match
        target_node = target_node.strip()

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


def create_nodes_and_relationship(uid, cid, concepts_dict=None, concepts_list=None, prerequisites=None,
                                  similarities=None):
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
            qid = concepts_dict[topic]['concept_id']
            question = concepts_dict[topic]['question']
            client.create_concept(cid, qid, topic, question)

    # Add concepts by list
    if concepts_list:
        for concept in concepts_list:
            if concept:
                concept_id = concept['concept_id']
                topic = concept['topic']
                question = concept['question']
                client.create_concept(cid, concept_id, topic, question)

    if prerequisites and prerequisites is not {}:
        for qid in prerequisites.keys():
            prerequisites_for_qid = prerequisites[qid]
            for pid in prerequisites_for_qid:
                client.create_prerequisite_relationship(qid, pid)

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
