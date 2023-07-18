from flask import request, Blueprint, jsonify

from graphdb.client import Neo4jClient
from logger import log_info

"""
queries

1. Retrieve all teachers in the graph.
2. Find the teacher with the ID variable 'teacher_id'.
3. List all courses in the graph.
4. Get the course with the ID variable 'course_id'.
5. Find all concepts in the graph.
6. Get the concept with the ID variable 'concept_id'.
7. Find all courses owned by a specific teacher identified by the 'teacher_id' variable.
8. List all concepts associated with a specific course identified by the 'course_id' variable.
9. Find the owner (teacher) of a specific course identified by the 'course_id' variable.
10. Get the answer for a specific concept identified by the 'concept_id' variable.

"""

query_map = {
    # Admin-Only
    "all_teachers": "MATCH (t:Teacher) RETURN t",
    "all_courses": "MATCH (c:Course) RETURN c",
    "all_concepts": "MATCH (co:Concept) RETURN co",

    # Teacher-Specific
    "teacher_with_id": "MATCH (t:Teacher {teacher_id: $teacher_id}) RETURN t",
    "courses_owned_by_teacher": "MATCH (t:Teacher {teacher_id: $teacher_id})-[:OWNS]->(c:Course) RETURN c",
    "owner_of_course": "MATCH (t:Teacher)-[:OWNS]->(c:Course {course_id: $course_id}) RETURN t",

    # User-Allowed
    "course_with_id": "MATCH (c:Course {course_id: $course_id}) RETURN c",
    "concepts_for_course_limit": "MATCH (c:Course {course_id: $course_id})-[:has]->(co:Concept) RETURN co LIMIT $limit",
    "concepts_associated_with_course": "MATCH (c:Course {course_id: $course_id})-[:HAS]->(co:Concept) RETURN co",
    "concept_with_id": "MATCH (co:Concept {concept_id: $concept_id}) RETURN co",
    "concept_answer": "MATCH (co:Concept {concept_id: $concept_id}) RETURN co.que AS question, co.ans AS answer",

    # Deleting
    "delete_concepts_by_course_id": "MATCH (c:Course {course_id: $course_id})-[:HAS]->(concept) DETACH DELETE concept"
}

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

    query = query_map[query]
    client = Neo4jClient()

    log_info(f'Calling {query}', parameters)
    result = client.run_query(query, **parameters)

    if result is not None:
        log_info(f'Result', result)
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Failed to run query'}), 400

