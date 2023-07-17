import uuid

from flask import Blueprint, request, jsonify

from graphdb.client import Neo4jClient
from logger import log_error, log_info
from tools.chatgpt import chat_with_open_ai
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

    if isinstance(qna, str):
        qna = extract_qna_list_from_string(qna)
        log_info('Found QnA from text', qna)

        # task = "embedding text knowledge into graph db"
        converstation = [
            {'role': 'system',
             'content': f'You are helpful tutor AI whose job is to embed text knowledge into graph database.'
                        f'The goal is to create concepts as nodes. Each concept can have a question with an answer.'
                        f'Given a list of concepts, find relationships between the concepts.'
                        f'Respond with these relationship in following format.'
                        f'A--PREREQUISITE-->B'
                        f'C--POSTREQUISITE-->B'
                        f'C--SIMILARITY--0.8-->B'},
            {'role': 'user', 'content': qna}
        ]

        relationships = chat_with_open_ai(conversation=converstation, temperature=1)
        log_info('Generated relationship', relationships)

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
        for q in qna:
            qid = str(uuid.uuid4())
            # TODO: Generate Pre-requisites here using LLM
            client.create_concept(qid, q.get('question'), q.get('answer'), cid, )

    except Exception as e:
        log_error('Failed to upload qna', e)

    return jsonify({'message': 'Course updated.'}), 200
