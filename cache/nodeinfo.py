from cachetools import TTLCache


MAX_CONVO_LENGTH = 100


class NodeInfoCache(object):  # Singleton
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = TTLCache(maxsize=200, ttl=36000)
        return cls._instance

    @staticmethod
    def exists(key):
        if not NodeInfoCache._instance:
            NodeInfoCache()
        return NodeInfoCache._instance.get(key)

    @staticmethod
    def setExists(key, data=True):
        if not NodeInfoCache._instance:
            NodeInfoCache()
        NodeInfoCache._instance[key] = data
