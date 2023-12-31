from graphdb.client import Neo4jClient
from logger import log_info, log_error

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

    # Learning
    "first_concept": "MATCH (c:Course {course_id: $course_id})-[:HAS]->(co:Concept) "
                     "WITH co, [(p)-[:PREREQUISITE_OF]->(co) | p] AS prerequisites "
                     "ORDER BY size(prerequisites) "
                     "RETURN co",
    "next_concept": "MATCH (c:Concept {concept_id: $concept_id})-[:PREREQUISITE_OF]->(co) " 
                    "RETURN co",

    # Deleting
    "delete_concepts_by_course_id": "MATCH (c:Course {course_id: $course_id})-[:HAS]->(concept) DETACH DELETE concept"
}


def run_query(query, parameters):
    cypher_query = query_map[query]
    client = Neo4jClient()

    log_info(f'Calling {cypher_query}', parameters)
    try:
        result = client.run_query(cypher_query, **parameters)

        if result:
            if isinstance(result, list):
                return [r.get('t') or r.get('c') or r.get('co') for r in result]
            else:
                return result.get('t') or result.get('c') or result.get('co')
        else:
            return None
    except Exception as e:
        log_error(f'Failed to run query {query}: {e}')
        return None


def get_all_concepts(cid):
    parameters = {}
    if cid:
        parameters['course_id'] = cid

    result = run_query("concepts_associated_with_course", parameters)
    return result or []
