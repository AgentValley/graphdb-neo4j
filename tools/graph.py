import re


def parse_relationships_string_with_regex(relationships_string):
    prerequisites = {}
    similarities = {}

    relationship_pattern = r'(\S+)--(PREREQUISITE|SIMILARITY)(--(?:\S+|\d+\.\d+))?-->(\S+)'
    matches = re.findall(relationship_pattern, relationships_string)

    for match in matches:
        source_node, relationship_type, value, target_node = match
        target_node = target_node.strip()

        if relationship_type == "PREREQUISITE":
            if target_node not in prerequisites:
                prerequisites[target_node] = [source_node]
            else:
                prerequisites[target_node].append(source_node)
        elif relationship_type == "SIMILARITY":
            similarity_value = float(value)
            if target_node not in similarities:
                similarities[target_node] = {source_node: similarity_value}
            else:
                similarities[target_node][source_node] = similarity_value

    return prerequisites, similarities

