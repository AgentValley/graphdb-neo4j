from flask import request, Blueprint, jsonify

from logger import log_info
from tools.query import query_map, run_query

query_bp = Blueprint('query', __name__)


# Define the route to execute the queries
@query_bp.route('/<string:query>', methods=['GET'])
def query_knowledge_graph(query):
    if query not in query_map:
        return jsonify({"error": "Invalid query key"}), 400

    uid = request.args.get('uid')
    student_id = request.args.get('student_id')
    cid = request.args.get('cid')
    qid = request.args.get('qid')
    limit = request.args.get('limit')

    parameters = {}
    if uid: parameters['teacher_id'] = uid
    if student_id: parameters['student_id'] = student_id
    if cid: parameters['course_id'] = cid
    if qid: parameters['concept_id'] = qid
    if limit: parameters['limit'] = limit

    result = run_query(query, parameters)

    if result is not None:
        log_info(f'Result', result)
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to run query'}), 400

