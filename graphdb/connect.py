from const import NEO4J_USERNAME, NEO4J_URI, NEO4J_PASSWORD
from logger import log_error


def connect_to_neo4j_driver():
    from neo4j import GraphDatabase

    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
            driver.verify_connectivity()
            return driver
    except Exception as e:
        log_error('Failed to connect to Neo4j', e)
        return None
