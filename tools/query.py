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


def run_query(query, parameters):
    query = query_map[query]
    client = Neo4jClient()

    log_info(f'Calling {query}', parameters)
    result = client.run_query(query, **parameters)

    return result


def get_all_concepts(cid):
    parameters = {}
    if cid: parameters['course_id'] = cid

    result = run_query("concepts_associated_with_course", parameters)
    if result:
        return [co.get('co') for co in result]
    else:
        return []
