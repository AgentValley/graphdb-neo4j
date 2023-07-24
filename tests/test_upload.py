from tools.chatgpt import get_relationships_among_concepts
from tools.graph import parse_relationships_string_with_regex
from tools.qna import extract_concepts_from_string

if __name__ == "__main__":
    qna = """
    
    """

    concepts_dict = extract_concepts_from_string(qna)
    relationship_str = get_relationships_among_concepts(concepts_dict)
    prerequisites, similarities = parse_relationships_string_with_regex(relationship_str)