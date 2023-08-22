from flask import Blueprint, request, jsonify

from logger import log_error
from tools.graph import get_relationships_among_concepts
from tools.graph import parse_relationships_string_with_regex, create_nodes, create_prerequisite_relationship, \
    create_similarity_relationship
from tools.qna import extract_concepts_from_string

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/qna', methods=['POST'])
def upload_qna_to_knowledge_graph():
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
        create_nodes(uid, cid, concepts_dict=concepts_dict)
        create_prerequisite_relationship(prerequisites)
        create_similarity_relationship(similarities)
    except Exception as e:
        log_error('Failed to upload qna', e)
        return jsonify({'error': f'Failed to upload qna. {e}'}), 200

    return jsonify({'response': 'Course updated.'}), 200


@upload_bp.route('/concept', methods=['POST'])
def upload_concept_to_knowledge_graph():
    uid = request.json.get('uid')
    cid = request.json.get('cid')
    qid = request.json.get('qid')
    topic = request.json.get('topic')
    weightage = request.json.get('weightage')
    question = request.json.get('question')
    prerequisites = request.json.get('prerequisites')
    if isinstance(prerequisites, str):
        prerequisites = prerequisites.split(',')

    if not qid:
        return jsonify({'error': 'qid not found. Add qid of the concept.'}), 400
    if not cid:
        return jsonify({'error': 'cid not found. Add cid of the concept.'}), 400
    if not topic:
        return jsonify({'error': 'topic not found. Add topic of the concept.'}), 400
    if not question:
        return jsonify({'error': 'question not found. Add question of the concept.'}), 400

    # existing_concepts = list(get_all_concepts(cid)) or []
    new_concept = {'concept_id': qid, 'topic': topic, 'question': question, 'weightage': weightage}
    # weightage = find_weightage_of_concepts(new_concept, existing_concepts)
    # new_concept['weightage'] = weightage

    # old_with_new_concepts.append(new_concept)

    # prerequisite_rel_str = find_prerequisite_relationship_of_concept(new_concept, existing_concepts)
    # prerequisites = parse_prerequisite_relationships_string_with_regex(prerequisite_rel_str, new_concept)
    # relationship_str = get_relationships_among_concepts(concepts_list=old_with_new_concepts)
    # prerequisites, similarities = parse_relationships_string_with_regex(relationship_str)
    try:
        create_nodes(uid, cid, concepts_list=[new_concept])
        create_prerequisite_relationship(qid, prerequisites)
    except Exception as e:
        log_error('Failed to upload qna', e)
        return jsonify({'error': f'Failed to upload qna. {e}'}), 200

    return jsonify({'response': 'Course updated.'}), 200
