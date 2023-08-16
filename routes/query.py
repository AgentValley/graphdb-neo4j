from flask import request, Blueprint, jsonify

from graphdb.client import Neo4jClient
from logger import log_info
from tools.query import query_map

query_bp = Blueprint('query', __name__)


# Define the route to execute the queries
@query_bp.route('/<string:query>', methods=['GET'])
def run_query(query):
    if query not in query_map:
        return jsonify({"error": "Invalid query key"}), 400

    uid = request.args.get('teacher_id')
    cid = request.args.get('course_id')
    qid = request.args.get('concept_id')
    limit = request.args.get('limit')

    parameters = {}
    if uid: parameters['teacher_id'] = uid
    if cid: parameters['course_id'] = cid
    if qid: parameters['concept_id'] = qid
    if limit: parameters['limit'] = limit

    result = run_query(query, parameters)

    if result is not None:
        log_info(f'Result', result)
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to run query'}), 400

