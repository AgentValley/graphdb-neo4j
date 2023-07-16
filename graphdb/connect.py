from logger import log_error


def connect_to_neo4j_driver():
    from neo4j import GraphDatabase

    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    URI = "neo4j://127.0.0.1"
    AUTH = ("neo4j", "agentvalley")

    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            return driver
    except Exception as e:
        log_error('Failed to connect to Neo4j', e)
        return None
