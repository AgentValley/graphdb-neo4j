import re

from tools.chatgpt import chat_with_open_ai

from neo4j.connect import connect_to_neo4j_driver
from tools.serializer import convert_node_to_object, convert_obj_to_string


def query_graph_db(query):
    driver = connect_to_neo4j_driver()
    cypher_query = convert_to_cypher(query)

    try:
        records, summary, keys = driver.execute_query(
            cypher_query,
            database_="neo4j",
        )

        # Loop through results and do something with them
        for item in records:
            # print(item)
            obj = convert_node_to_object(item[0] if list(item) else item)
            # print(obj)
            data = convert_obj_to_string(obj)
            print(data)

    except Exception as e:
        print(e)


def save_to_graph_db(text):
    driver = connect_to_neo4j_driver()

    # Convert NL query to Cypher
    cypher_query = convert_to_cypher(text, add_or_update=True)
    print("CYPHER:\n", cypher_query)

    driver.execute_query(
        cypher_query,
        database_="neo4j",
    )


def convert_to_cypher(query, add_or_update=False):
    task = "embedding text knowledge into graph db" if add_or_update else "extracting knowledge from graph db."
    converstation = [
        {'role': 'system',
         'content': f'You help in {task}'
                    f'the goal is to identify nodes objects and edge relationship from the given '
                    f'text. Return your answer in Cypher query format for Neo4j. The response '
                    f'should contain only the Cypher queries and nothing else.'},
        {'role': 'system', 'content': query}
    ]

    response = chat_with_open_ai(conversation=converstation, temperature=1)
    # response = """
    #     The given text contains information about the planet Mars and its characteristics. To represent this
    #     information in a graph, we can create nodes for the objects mentioned (e.g., "Mars", "sun", "world",
    #     "earth", "surface") and specify relationships between them (e.g., "revolves about", "receives light and
    #     heat from", "older than", "cooled to", "necessary for").
    #
    #     Here is an example of how the text can be represented in Cypher queries:
    #
    #     1. Create nodes:
    #     ```
    #     CREATE (:Planet {name: "Mars"})
    #     CREATE (:CelestialBody {name: "Sun"})
    #     CREATE (:CelestialBody {name: "Earth"})
    #     CREATE (:Surface {name: "MarsSurface"})
    #     ```
    #
    #     2. Specify relationships:
    #     ```
    #     MATCH (mars:Planet {name: "Mars"})
    #     MATCH (sun:CelestialBody {name: "Sun"})
    #     CREATE (mars)-[:REVOLVES_ABOUT]->(sun)
    #
    #     MATCH (mars)-[:REVOLVES_ABOUT]->(sun)
    #     SET mars.meanDistance = 140000000
    #
    #     MATCH (mars)-[:RECEIVES_LIGHT_AND_HEAT_FROM]->(sun)
    #     SET mars.lightHeatReceived = (sun.lightHeatReceived / 2)
    #
    #     MATCH (mars)-[:OLDER_THAN]->(earth:CelestialBody {name: "Earth"})
    #
    #     MATCH (mars)-[:COOLED_TO]->(temperature:Temperature)
    #     SET temperature.value = (lifeTemperature - 100)
    #
    #     MATCH (mars:Planet {name: "Mars"})
    #     MATCH (surface:Surface {name: "MarsSurface"})
    #     CREATE (mars)-[:HAS_SURFACE]->(surface)
    #
    #     MATCH (surface:Surface {name: "MarsSurface"})
    #     SET surface.hasAir = true, surface.hasWater = true
    #     ```
    #
    #     Note: The above queries assume that there are additional nodes and relationships
    #     already present in the graph, such as the definitions of "Temperature", "Surface",
    #     and other celestial bodies. Adjustments may be needed based on the existing data model.
    # """
    queries = extract_cypher_queries(response)
    return "\n".join(queries)


def extract_cypher_queries(text):
    pattern = r"((CREATE|MATCH|OPTIONAL MATCH|WHERE|RETURN|CREATE|DELETE|SET|REMOVE|WITH|ORDER BY|SKIP|LIMIT|" \
              r"UNION|CALL|FOREACH|MERGE|UNWIND)\b.*?(?=\n|\Z))"
    queries = re.findall(pattern, text, )
    return list(q[0] for q in queries)
