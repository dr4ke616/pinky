import re


class Cache(dict):

    def set(self, key, value):
        self[key] = value

    def get(self, key):
        return super(Cache, self).get(key)

    def mget(self, keys):
        return [self.get(k) for k in keys]

    def delete(self, key):
        try:
            del self[key]
        except:
            pass

    def keys(self, pattern):
        retval = []
        regex = re.compile(pattern.replace('*', '(.*)'))
        for key in super(Cache, self).keys():
            match = regex.match(key)
            if match:
                for gr in match.groups():
                    retval.append(key.replace('*', gr))
        return retval