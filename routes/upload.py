from flask import Blueprint, request, jsonify

from flask import Blueprint, request, jsonify

from logger import log_error
from tools.chatgpt import get_relationships_among_concepts
from tools.graph import parse_relationships_string_with_regex, create_nodes_and_relationship
from tools.qna import extract_concepts_from_string

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('', methods=['POST'])
def upload_to_knowledge_graph():
    uid = request.json.get('uid')
    cid = request.json.get('cid')
    qna = request.json.get('qna')

    if not uid:
        return jsonify({'error': 'uid not found. Add uid of the owner of the course.'}), 400
    if not cid:
        return jsonify({'error': 'cid not found. Add cid of the course.'}), 400
    if not qna:
        return jsonify({'error': 'qna not found. Add list of qna to add to the course.'}), 400

    concepts_dict = {}
    prerequisites = {}
    similarities = {}
    if isinstance(qna, str):
        concepts_dict = extract_concepts_from_string(qna)
        relationship_str = get_relationships_among_concepts(concepts_dict)
        prerequisites, similarities = parse_relationships_string_with_regex(relationship_str)

    elif not isinstance(qna, list):
        log_error('Failed to process QnA, not a list, expecting str or list', qna)
        return jsonify({'error': 'qna invalid, needs to be list of {"question": <q1>, "answer": <a1>}.'}), 400

    try:
        create_nodes_and_relationship(uid, cid, concepts_dict, prerequisites, similarities)
    except Exception as e:
        log_error('Failed to upload qna', e)
        return jsonify({'error': f'Failed to upload qna. {e}'}), 200

    return jsonify({'response': 'Course updated.'}), 200
