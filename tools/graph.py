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
            similarity_value = float(value.split('--')[1])
            if target_node not in similarities:
                similarities[target_node] = {source_node: similarity_value}
            else:
                similarities[target_node][source_node] = similarity_value

    return prerequisites, similarities

if __name__ == "__main__":
    s = '22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->a0b94d13-1f0f-458e-8f34-3ddcef83c33f\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->cc24ee53-00f8-462a-b306-97d1204b50c1\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->d7a3d7aa-e4fb-42e6-9752-286ba4256cf6\n22e5b338-089c-4b00-af53-f1ba913f48fa--SIMILARITY--0.6-->a19689159-1b90-43e0-b640-6a22bc0f5ab6'
    result = parse_relationships_string_with_regex(s)
    print(result)

