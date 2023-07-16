from example import *


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        # create_teacher()
        # create_course()
        #
        # # add_concept()
        # add_concepts()
        #

        # Find map of all the concepts
        # next = find_concepts_no_pre()
        # pre = []
        # while len(next):
        #     print("Next ->", [x.get('concept_id') for x in next])
        #     pre.extend(next)
        #     next = find_concepts_with_pre([i.get('concept_id') for i in pre])
        #     # Filter out pre
        #     next = [n for n in next if n.get('course_id') in pre]
        #     print(next)

        # Find prerequisite
        # pre = find_prerequisites_of("c1")
        # print(pre)

        # students = [
        #     {"id": "student1", "taught": ["c1", "c2", "c3"], "known": ["c3", "c4"], "answered": ["c5"],
        #      "failed": ["c6"]},
        #     {"id": "student2", "taught": ["c2"], "known": ["c4", "c5"], "answered": ["c4", "c5", "c8"],
        #      "failed": ["c7"]},
        #     # Add more student attributes as needed
        # ]
        #
        # for student in students:
        #     student_id = student["id"]
        #     taught_concepts = student["taught"]
        #     known_concepts = student["known"]
        #     answered_concepts = student["answered"]
        #     failed_concepts = student["failed"]
        #     student = add_student_knowledge(student_id, taught_concepts, known_concepts, answered_concepts,
        #                                     failed_concepts)
        #     print(student)

        reset_all()

    except Exception as e:
        print(e)
        raise e

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
