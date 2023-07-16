import re

from logger import log_info


def extract_qna_list_from_string(text):
    # Regular expression pattern to match questions and answers
    pattern = r"Question:(.*?)(?=Answer:|$)(.*?)\n"

    # Extracting matches from the text
    matches = re.findall(pattern, text, re.DOTALL)

    # Constructing the list of dictionaries
    qa_list = [{"question": q.strip(), "answer": a.strip()} for q, a in matches]

    return qa_list
