import uuid

from flask import Blueprint, request, jsonify

from graphdb.client import Neo4jClient
from logger import log_error, log_info
from tools.chatgpt import chat_with_open_ai
from tools.graph import parse_relationships_string_with_regex
from tools.qna import extract_qna_list_from_string

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('', methods=['POST'])
def upload_to_knowledge_base():

    uid = request.json.get('uid')
    cid = request.json.get('cid')
    qna = request.json.get('qna')

    if not uid:
        return jsonify({'error': 'uid not found. Add uid of the owner of the course.'}), 400
    if not cid:
        return jsonify({'error': 'cid not found. Add cid of the course.'}), 400
    if not qna:
        return jsonify({'error': 'qna not found. Add list of qna to add to the course.'}), 400

    qna_with_id = {}
    prerequisites = {}
    similarities = {}
    if isinstance(qna, str):
        qna = extract_qna_list_from_string(qna)
        for i in range(0, len(qna)):
            qna_with_id[str(uuid.uuid4())] = qna[i]

        log_info('Found QnA from text', qna)

        # task = "embedding text knowledge into graph db"
        ids = qna_with_id.keys()
        qna_text = "\n\n".join([
            f"{i}: {qna_with_id[i].get('question', 'Empty')}\n"
            f"A{i}: {qna_with_id[i].get('answer', 'Empty')}" for i in ids
        ])
        converstation = [
            {'role': 'system',
             'content': f'You are helpful tutor AI whose job is to embed text knowledge into graph database.'
                        f'The goal is to create concepts as nodes. Each concept can have a question with an answer.'
                        f'Given a list of questions, find relationships between the questions.'
                        f'Respond with these relationship in following format.'
                        f'Q1--PREREQUISITE-->Q2'
                        f'Q3--SIMILARITY--0.8-->Q4'
                        f'where Q1, Q2, Q3... are the question number that denotes a questions, '
                        f'the relation PREREQUISITE denotes that Q1 has prerequisite Q1'
                        f'0.8 in SIMILARITY represets the similarity factor between Q3 and Q4.'
                        f'The value of SIMILARITY ranges from 0.1 to 1.0 where 1.0 means they are the same in meaning.'},
            {'role': 'user', 'content': qna_text}
        ]

        relationship_str = chat_with_open_ai(conversation=converstation, temperature=1)
        log_info('Generated relationship', relationship_str)
        prerequisites, similarities = parse_relationships_string_with_regex(relationship_str)

    elif not isinstance(qna, list):
        log_error('Failed to process QnA, not a list, expecting str or list', qna)
        return jsonify({'error': 'qna invalid, needs to be list of {"question": <q1>, "answer": <a1>}.'}), 400

    try:
        client = Neo4jClient()
        teacher = client.get_teacher(uid)
        if not teacher:
            log_info('Teacher does not exists', 'Creating Teacher')
            teacher = client.create_teacher(uid)
        log_info('Teacher', teacher)
        course = client.get_course(cid)
        if not course:
            log_info('Course does not exists', 'Creating Course')
            course = client.create_course_for_teacher(cid, uid)
        log_info('Course', course)
        # Add concepts
        ids = qna_with_id.keys()
        created_qids = []
        for qid in ids:
            q = qna_with_id[qid]
            client.create_concept(qid, q.get('question'), q.get('answer'), cid)

        if prerequisites is not {}:
            for qid in prerequisites.keys():
                prerequisites_for_qid = prerequisites[qid]
                for pid in prerequisites_for_qid:
                    client.create_prerequisite_relationship(qid, pid)
        if similarities is not {}:
            for qid in similarities.keys():
                similarities_for_qid = similarities[qid]
                for sid in similarities_for_qid.keys():
                    if similarities_for_qid.get(sid) is not None:
                        client.create_similarity_relationship(qid, sid, similarities_for_qid.get(sid))

    except Exception as e:
        log_error('Failed to upload qna', e)

    return jsonify({'message': 'Course updated.'}), 200
