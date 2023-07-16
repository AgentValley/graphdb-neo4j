import json

from tools.chatgpt import chat_with_open_ai


class Node:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Relationship:
    def __init__(self, start_node, end_node, relation_type, **kwargs):
        self.start_node = start_node
        self.end_node = end_node
        self.relation_type = relation_type
        for key, value in kwargs.items():
            setattr(self, key, value)


# Function to convert a Neo4j node into a readable object
def convert_node_to_object(node):
    properties = dict(node.items())

    # relations = get_node_relations(node)
    # for relation in relations:
    #     relation_properties = dict(relation.items())
    #     start_node = convert_node_to_object(relation.start_node)
    #     end_node = convert_node_to_object(relation.end_node)
    #     relation_obj = Relationship(start_node, end_node, relation.type, **relation_properties)
    #     setattr(obj, relation.type, relation_obj)
    return properties


def convert_obj_to_string(data):
    converstation = [
        {'role': 'system',
         'content': f'You help in displaying the knowledge of a neo4j node, which may contain'
                    f'attributes and relationships. The goal is to identify nodes objects and '
                    f'edge relationship from the given text. Return the answer in plain text.'
                    f'The response should contain only knowledge itself. No need to mention the term Node or relationship.'
                    f'Be concise.'},
        {'role': 'system', 'content': json.dumps(data)}
    ]

    response = chat_with_open_ai(conversation=converstation, temperature=1)
    # print(response)
    return response
