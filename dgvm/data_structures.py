
class Treect(object):

    def __init__(self, from_dict=None, **kwargs):

        self.__d = {}

        init_data = {}
        if from_dict:
            init_data.update(from_dict)

        init_data.update({k.replace('__', '/'): v for k, v in kwargs.iteritems()})

        for k, v in init_data.items():
            if isinstance(v, dict):
                self[k] = self.__class__(v)
            else:
                self[k] = v

    def set(self, key, val):
        self[key] = val

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def delete(self, item):
        del self.__d[item]

    def items(self):
        return self.__d.items()

    def __all_items(self, prefix=[]):
        for k, v in self.items():
            if isinstance(v, self.__class__):
                for k2, v2 in self.__class__.__all_items(v, prefix + [k]):
                    yield k2, v2
            else:
                yield '/'.join(prefix + [k]), v

    def all_items(self):

        return self.__all_items()

    def to_dict(self):

        d = {}
        for k, v in self.items():
            if isinstance(v, self.__class__):
                d[k] = v.to_dict()
            else:
                d[k] = v
        return d

    @classmethod
    def from_dict(cls, from_dict):
        return cls(from_dict)

    def __len__(self):
        return len(self.__d)

    def __getitem__(self, item):

        if not isinstance(item, (str, unicode)):
            return self.__d[item]

        keys = item.split('/')

        if len(keys) == 1:
            return self.__d[item]

        v = self
        for k in keys:
            v = v[k]

        return v

    def __setitem__(self, key, value):

        if not isinstance(key, (str, unicode)):
            self.__d[key] = value
            return

        keys = key.split('/')

        if len(keys) == 1:
            self.__d[key] = value
            return

        container = self
        for k in keys[:-1]:
            if k not in container:
                container[k] = self.__class__()
            container = container[k]

        container[keys[-1]] = value

    def __contains__(self, item):
        if not isinstance(item, (str, unicode)):
            return item in self.__d

        keys = item.split('/')

        if len(keys) == 1:
            return item in self.__d

        v = self
        try:
            for k in keys:
                v = v[k]
        except KeyError:
            return False

        return True

    def __delitem__(self, key):

        if not isinstance(key, (str, unicode)):
            del self.__d[key]
            return

        keys = key.split('/')

        if len(keys) == 1:
            del self.__d[key]
            return

        container = self
        for k in keys[:-1]:
            if k not in container:
                container[k] = self.__class__()
            container = container[k]

        del container[keys[-1]]

    def __iter__(self):
        return iter(self.__d)

    def __eq__(self, other):

        if isinstance(other, self.__class__):

            if len(self) != len(other):
                return False

            for k, v in self.items():
                if other.get(k) != v:
                    return False

            return True

        return NotImplemented

    def __ne__(self, other):

        if isinstance(other, self.__class__):

            return not self.__eq__(other)

        return NotImplemented

    def __repr__(self):

        return repr(self.__d)


# TODO: make Heap historical and collapseable,
# TODO: i.e. each commit is a new treect which fallsback to the last commit's treect on key not found.
class Heap(object):

    def __init__(self, size):
        super(Heap, self).__init__()
        self.size = size
        self.__data = Treect()

    def set(self, address, obj):
        if not isinstance(address, (int, str, unicode)):
            raise ValueError('Heap address must be of type int or string, not ' + type(address).__name__)
        self.__data[address] = obj

    def get(self, item, default=None):
        return self.__data.get(item, default)

    def delete(self, item):
        del self.__data[item]

    def percent_used(self):
        return float(len(self.__data)) / float(self.size) * 100

    def __len__(self):
        return len([None for _ in self.__data.all_items()])

    def __getitem__(self, item):
        return self.__data[item]

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __delitem__(self, key):
        del self.__data[key]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<Heap object at %s, %s%% used, with size=%s>' % (id(self), self.percent_used(), self.size)

    def dump(self):
        print
        for k, v in self.__data.items():
            print ('%s \t %s' % (k, v)).expandtabs(40)
        print
