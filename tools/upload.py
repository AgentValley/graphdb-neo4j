from graphdb.client import Neo4jClient
from logger import log_error

client = Neo4jClient()


def create_teacher(uid):
    try:
        client.create_teacher(uid)
        return True
    except Exception as e:
        log_error('Failed to create teacher', e)
        return False


def create_course(cid, tid):
    try:
        client.create_course(cid, tid)
        return True
    except Exception as e:
        log_error('Failed to create course', e)
        return False