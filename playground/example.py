import random

from graphdb.client import Neo4jClient

client = Neo4jClient()

teacher_id = "teacher123"


def create_teacher():
    # Create Teacher
    client.create_teacher(teacher_id)


def create_course(course_id="course123"):
    # Create Course with Teacher relationship
    course = client.create_course(course_id, teacher_id)
    print("Course created:", course)


def add_concept(course_id="course123"):
    # Add knowledge to the graph database
    question = "What is the capital of France?"
    answer = "The capital of France is Paris."
    concept = client.create_concept(question, answer, course_id, [])
    print("Concept created:", concept)


def add_concepts(course_id="course123"):
    # Create Concepts
    concepts = {}
    for i in range(1, 11):
        question = f"Question {i}"
        answer = f"Answer {i}"
        prerequisites = random.sample(list(concepts.keys()), random.randint(0, min(3, i - 1)))
        concept_id = f"c{i}"
        concept = client.create_concept(concept_id, question, answer, course_id, prerequisites)
        concepts[f"c{i}"] = concept
        print(f"Concept {i} created:", concept)


def find_concepts_with_pre(prerequisites=["c1", "c2", "c3"]):
    # Find Concepts with Given Prerequisites
    concepts_with_prerequisites = client.find_concepts_with_prerequisites(prerequisites)
    print("Concepts with given prerequisites:")
    for concept in concepts_with_prerequisites:
        print(concept)
    return concepts_with_prerequisites


def find_concepts_no_pre():
    # Find concepts to teach
    concepts_without_prerequisites = client.find_concepts_without_prerequisites()
    # print("Concepts without prerequisites:")
    # for record in concepts_without_prerequisites:
    #     concept = record["c"]
    #     print(concept)
    return concepts_without_prerequisites


def find_prerequisites_of(course_id):
    prerequisites = client.find_prerequisites(course_id)

    return prerequisites


def add_student_knowledge(student_id, taught_concepts, known_concepts, answered_concepts, failed_concepts):
    client.add_student_knowledge(student_id, taught_concepts, known_concepts, answered_concepts, failed_concepts)
    print("Student knowledge added.")


def reset_all():
    data = client.reset()
    print("Reset complete", data)
