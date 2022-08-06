
import re
from itertools import zip_longest
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


PROPERTIES = ["spot", "base", "entity", "@id", "@type", "@context"]
reg = re.compile(r"([\w_@#$]+)")


def wind(values, name=None, source=None, list_separator=True, separator=None):
    """
    Если list_separator=False - цифры будут восприниматься как ключи, а не индекс
    """
    r = source or dict()

    if name is not None:
        if name not in source:
            source[name] = {}
        r = source[name]
    null_count = 0
    for key, value in values.items():
        current = r
        if separator is None:
            sub_keys = reg.findall(key)
        else:
            sub_keys = key.split(separator)

        for sk1, sk2 in zip_longest(sub_keys, sub_keys[1:]):
            if sk1.isdigit() and list_separator:
                sk1 = int(sk1)
                if sk2 is None:
                    current[sk1] = value
                    null_count -= 1
                    break

                if current[sk1] is None:
                    if sk2.isdigit():
                        n = (int(sk2) + 1)
                        null_count += n - 1
                        current[sk1] = [None] * n
                    else:
                        null_count -= 1
                        current[sk1] = {}
            else:
                if sk2 is None:
                    current[sk1] = value
                    break

                if sk1 not in current:
                    if sk2.isdigit() and list_separator:
                        n = (int(sk2) + 1)
                        null_count += n
                        current[sk1] = [None] * n
                    else:
                        current[sk1] = {}

            if sk2.isdigit() and len(current[sk1]) <= int(sk2) and list_separator:
                n = (int(sk2) - len(current[sk1]) + 1)
                null_count += n
                current[sk1].extend([None] * n)

            current = current[sk1]
    if null_count > 0:
        raise Exception()
    return r


def join_list_key(key, name, list_separator):
    if list_separator == "[]":
        return "".join([name, "[", str(key), "]"])
    else:
        return list_separator.join([name, str(key)])


def join_dict_key(key, name, list_separator):
    return list_separator.join([name, key])


def unwind(values, name=None, result=None, list_separator="."):
    if result is None:
        result = {}

    if isinstance(values, list):
        iterator = enumerate(values)
        join_key = join_list_key
    elif isinstance(values, dict):
        iterator = values.items()
        join_key = join_dict_key
    else:
        return

    for key, value in iterator:
        if name is None:
            _name = str(key)
        else:
            _name = join_key(key, name, list_separator)

        if value and (type(value) == dict or type(value) == list):
            result = unwind(value, _name, result, list_separator=list_separator)
        else:
            result[_name] = value

    return result


def uri2target(value: str) -> dict:
    schema, data = value.split(":", 1)
    url = urlsplit("{schema}://{url}".format(schema=schema, url=data.lstrip("/")))
    entity = url.username
    if entity is not None and entity[0] == "[" and entity[-1] == "]":
        items = list(filter(lambda x: x.strip() != '', map(str.strip, entity.strip("[]").strip().split(","))))
        if len(items) > 1:
            if str(items[0])[0] == '"':
                entity = [x.strip('"') for x in items]
            else:
                entity = [int(x) for x in filter(str.isdigit, items)]
    context = wind(dict(parse_qsl(url.query)))
    return {
        "spot": url.scheme,
        "base": url.hostname,
        "entity": entity,
        "@id": url.fragment if url.fragment != '' else None,
        "@type": url.path if url.path != '' else None,
        "@context": context if len(context) > 0 else None
    }


class Target:
    spot = None
    base = None
    entity = None

    _id = None
    _context = None
    _type = None

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            items = dict(zip(PROPERTIES, args))
        elif len(args) == 1 and isinstance(args[0], (str, dict)):
            items = uri2target(args[0]) if isinstance(args[0], str) else args[0]
        else:
            items = {}
        items.update(kwargs)
        for k in PROPERTIES:
            setattr(self, k.replace("@", "_"), items.get(k))

    def __eq__(self, value):
        """ Return self==value. """
        return str(self) == str(value)

    def __len__(self) -> int:
        return len(self.as_dict)

    def __iter__(self):
        # now 'yield' through the items
        for x, y in self.as_dict.items():
            yield x, y

    def __getitem__(self, name: str):
        if name in PROPERTIES:
            return getattr(self, name.replace("@", "_"))
        else:
            raise Exception("Unknown property: {}".format(name))

    def __setitem__(self, name: str, value):
        if name in PROPERTIES:
            setattr(self, name.replace("@", "_"), value)
        else:
            raise Exception("Unknown property: {}".format(name))

    def __delitem__(self, name: str):
        if name in PROPERTIES:
            setattr(self, name.replace("@", "_"), None)
        else:
            raise Exception("Unknown property: {}".format(name))

    def __contains__(self, name: str):
        return name in PROPERTIES and getattr(self, name.replace("@", "_")) is not None

    @classmethod
    def dict(cls, value: dict):
        return cls(**value)

    @classmethod
    def str(cls, value: str):
        return cls(**uri2target(value))

    def unwind(self, name=None):
        return unwind(self.as_dict, name)

    def clear(self):
        self.spot, self.base, self.entity = None, None, None
        self._id, self._context, self._type = None, None, None

    def __str__(self):
        entity = self.entity
        if isinstance(entity, list):
            if isinstance(entity[0], str):
                entity = '["%s"]' % '","'.join(entity)
            else:
                entity = '[%s]' % ','.join(map(str, entity))
        result = urlunsplit([
            self.spot or '',
            self.base if entity is None else str(entity) + "@" + str(self.base or ''),
            self._type or '',
            urlencode(unwind(self._context), doseq=False) if self._context is not None else {},
            self._id or ''
        ])
        return result.replace("://", ":", 1) if self.spot not in ["http", "https"] else result

    @property
    def as_dict(self):
        result = {}
        for k, v in self.__dict__.copy().items():
            k = k.replace("_", "@")
            if k in PROPERTIES and v:
                result[k] = v
        return result

    def child(self, entity):
        return Target(spot=self.base, base=self.entity, entity=entity)


class Targets(list):
    def __init__(self, *args, unique: bool = False, **kwargs):
        _all = [Target(x) if not isinstance(x, Target) else x for x in args[0]] if len(args) > 0 else []
        if unique:
            _init = []
            for i in _all:
                if not self.contains(_init, i):
                    _init.append(i)
        else:
            _init = _all
        super(Targets, self).__init__(_init)
        self._unique = unique

    @staticmethod
    def contains(items: list, item: Target):
        return str(item) in list(map(str, items))

    def __contains__(self, value: Target):
        return self.contains(self, value)

    def insert(self, index, value: Target) -> Target:
        if not self._unique:
            super().insert(index, value)
        elif value not in self:
            super().insert(index, value)
        else:
            i = super().index(value)
            value = self[i]
            del self[i]
            super().insert(index, value)
        return value

    def append(self, value: Target) -> Target:
        if not self._unique:
            super().append(value)
            return value
        elif value not in self:
            super().append(value)
            return value
        else:
            return self[super().index(value)]

    @property
    def dictionaries(self):
        return self._template(self, "#DICTIONARY")

    @property
    def strings(self):
        return self._template(self, "#STRING")

    @property
    def spots(self):
        return self._template(self, "SPOT")

    @property
    def bases(self):
        return self._template(self, "BASE")

    @property
    def entities(self):
        return self._template(self, "ENTITY")

    @staticmethod
    def _template(value, name=None):
        f = {
            "#DICTIONARY": lambda x: dict(x),
            "#STRING": lambda x: str(x),
            "SPOT": lambda x: x.spot,
            "BASE": lambda x: x.base,
            "ENTITY": lambda x: x.entity
        }
        name = str(name).upper() if name is not None and str(name).upper() in f.keys() else "#STRING"
        if isinstance(value, list):
            return [f[name](i) for i in value]
        else:
            return f[name](value)
