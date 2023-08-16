import re
import uuid

from logger import log_warn


def extract_qna_list_from_string(text):
    # Regular expression pattern to match questions and answers
    pattern = r"Topic:(.*?)Question:(.*?)(?=Answer:|$)(.*?)\n"

    # Extracting matches from the text
    matches = re.findall(pattern, text, re.DOTALL)
    if len(matches) == 0:
        log_warn('Failed to extract QnA from given text', text)

    # Constructing the list of dictionaries
    qa_list = [{"topic": c.strip(), "question": q.strip(), "answer": a.strip()} for c, q, a in matches]

    return qa_list


def extract_concepts_from_string(text):
    # Regular expression pattern to match questions and answers
    pattern = r"Topic:(.*?)Question:(.*?)(?=Answer:|$)(.*?)\n"

    # Extracting matches from the text
    matches = re.findall(pattern, text, re.DOTALL)
    if len(matches) == 0:
        log_warn('Failed to extract QnA from given text', text)

    concept_dicts = {}
    for c, q, a in matches:
        if c.strip() not in concept_dicts:
            concept_dicts[c.strip()] = {
                "concept_id": str(uuid.uuid4()),
                "title": c.strip(),
                "questions": [{"question": q.strip(), "answer": a.strip()}]
            }
        else:
            concept_dicts[c.strip()]["questions"].append({"question": q.strip(), "answer": a.strip()})

    return concept_dicts
