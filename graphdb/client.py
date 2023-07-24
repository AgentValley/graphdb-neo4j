from graphdb.connect import connect_to_neo4j_driver
from logger import log_error, log_info


class Neo4jClient:
    _instance = None

    # Singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.driver = connect_to_neo4j_driver()

    def run_query(self, query, **params):
        try:
            with self.driver.session() as session:
                result = session.run(query, **params)
                return result.data()
        except Exception as e:
            log_error('Failed to execute query', e)
            return None

    def get_teacher(self, teacher_id):
        query = "MATCH (t:Teacher {teacher_id: $teacher_id}) RETURN t"
        parameters = {"teacher_id": teacher_id}
        return self.run_query(query, **parameters)

    def create_teacher(self, teacher_id):
        query = "MERGE (t:Teacher {teacher_id: $teacher_id}) RETURN t"
        parameters = {"teacher_id": teacher_id}
        return self.run_query(query, **parameters)

    def get_course(self, course_id):
        query = "MATCH (c:Course {course_id: $course_id}) RETURN c"
        parameters = {"course_id": course_id}
        return self.run_query(query, **parameters)

    def create_course_for_teacher(self, course_id, teacher_id):
        teacher = self.get_teacher(teacher_id)
        query = "MATCH (t:Teacher {teacher_id: $teacher_id}) " \
                "CREATE (c:Course {course_id: $course_id}) " \
                "MERGE (t)-[:OWNS]->(c) " \
                "RETURN c"
        parameters = {"course_id": course_id, "teacher_id": teacher_id}
        return self.run_query(query, **parameters)

    def create_concept(self, concept_id, concept, questions, course_id, prerequisites=None):
        query = "MATCH (c:Course {course_id: $course_id}) " \
                "MERGE (co:Concept {concept_id: $concept_id, concept: $concept}) " \
                "MERGE (c)-[:HAS]->(co) " \
                "RETURN co"
        parameters = {"course_id": course_id, "concept_id": concept_id, "concept": concept}
        with self.driver.session() as session:
            result = session.run(query, parameters)
            single = result.single()
            concept = single["co"] if single else None
            if prerequisites:
                for prerequisite_id in prerequisites:
                    self.create_prerequisite_relationship(concept_id, prerequisite_id)
        return concept

    def create_prerequisite_relationship(self, concept_id, prerequisite_id):
        query = "MATCH (c:Concept {concept_id: $concept_id}), (p:Concept {concept_id: $prerequisite_id}) " \
                "MERGE (c)-[:PREREQUISITE_OF]->(p)"
        parameters = {"concept_id": concept_id, "prerequisite_id": prerequisite_id}
        return self.run_query(query, **parameters)

    def create_similarity_relationship(self, concept_id, similarity_id, value):
        query = "MATCH (c:Concept {concept_id: $concept_id}), (p:Concept {concept_id: $similarity_id}) " \
                "MERGE (sim:Similarity {value: $value}) " \
                "MERGE (c)-[:SIMILARITY]->(sim)-[:SIMILARITY_OF]->(p)"
        parameters = {"concept_id": concept_id, "similarity_id": similarity_id, "value": value}
        log_info('Create Similarity Relationship', parameters)
        return self.run_query(query, **parameters)

    def find_prerequisites(self, concept_id):
        query = """
        MATCH (c:Concept {concept_id: $concept_id})<-[:PREREQUISITE_OF]-(p:Concept)
        RETURN p
        """
        parameters = {"concept_id": concept_id}
        with self.driver.session() as session:
            result = session.run(query, parameters)
            data = result.data()
            return [d['p'] for d in data]

    def find_concepts_without_prerequisites(self):
        query = "MATCH (c:Concept) WHERE NOT (:Concept)-[:PREREQUISITE_OF]->(c) RETURN c"
        with self.driver.session() as session:
            result = session.run(query)
            data = result.data()
            return [d['c'] for d in data]

    def find_concepts_with_prerequisites(self, prerequisites):
        query = """
            MATCH (c:Concept)-[:PREREQUISITE_OF]->(p:Concept)
            WHERE ALL(prerequisite_id IN c.concept_id
                      WHERE prerequisite_id IN $prerequisites)
            RETURN p
        """
        parameters = {"prerequisites": prerequisites}
        with self.driver.session() as session:
            result = session.run(query, parameters)
            data = result.data()
            return [d['p'] for d in data]

    def add_student_knowledge(self, student_id, taught_concepts, known_concepts, answered_concepts, failed_concepts):
        query = """
            MERGE (s:Student {student_id: $student_id})
            
            WITH s
            UNWIND $taught_concepts AS taught_concept
            MATCH (tc:Concept {concept_id: taught_concept})
            MERGE (s)-[:HAS_BEEN_TAUGHT]->(tc)

            WITH s
            UNWIND $known_concepts AS known_concept
            MATCH (kc:Concept {concept_id: known_concept})
            MERGE (s)-[:KNOWS]->(kc)
            
            WITH s
            UNWIND $answered_concepts AS answered_concept
            MATCH (ac:Concept {concept_id: answered_concept})
            MERGE (s)-[:ANSWERED]->(ac)
            
            WITH s
            UNWIND $failed_concepts AS failed_concept
            MATCH (fc:Concept {concept_id: failed_concept})
            MERGE (s)-[:FAILED_TO_ANSWER]->(fc)
            RETURN s
        """
        parameters = {
            "student_id": student_id,
            "taught_concepts": taught_concepts,
            "known_concepts": known_concepts,
            "answered_concepts": answered_concepts,
            "failed_concepts": failed_concepts
        }

        with self.driver.session() as session:
            result = session.run(query, parameters)
            data = result.data()
            return [d['s'] for d in data]

    def reset(self):
        teacher_query = "MATCH (t:Teacher) DETACH DELETE t"
        course_query = "MATCH (c:Course) DETACH DELETE c"
        concept_query = "MATCH (c:Concept) DETACH DELETE c"
        student_query = "MATCH (s:Student) DETACH DELETE s"

        with self.driver.session() as session:
            session.run(teacher_query)
            session.run(course_query)
            session.run(concept_query)
            session.run(student_query)

# Example usage
