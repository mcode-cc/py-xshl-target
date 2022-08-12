import json
from networkx import topological_sort
import unittest
from xshl.target import Target, Reference, GRoot, wind, unwind


class TestMethods(unittest.TestCase):
    def test_target_contains(self):
        t = Target(spot="baz", base="bar", entity="foo")
        self.assertTrue("spot" in t)

    def test_target_attr(self):
        t = Target("https://en.wikipedia.org/wiki/Object_database")
        self.assertTrue(t["@type"] == "/wiki/Object_database")
        self.assertTrue(t.spot == "https")

    def test_target_context(self):
        t = Target("https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets")
        self.assertTrue(t["@context"]["value"]["text"] == "Targets")

    def test_target_eq(self):
        t0 = Target("https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets")
        t1 = Target(
            {'spot': 'https', 'base': 'translate.yandex.ru', '@type': '/',
             '@context': {'value': {'lang': 'en-ru', 'text': 'Targets'}}}
        )
        self.assertTrue(t0 == t1)
        t0.entity = "user"
        self.assertFalse(t0 == t1)

    def test_target_str(self):
        url = "https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets"
        t = Target(url)
        t["@id"] = "aaa"
        self.assertTrue(t["@context"]["value"]["text"] == "Targets")
        self.assertTrue(str(t) == url + "#aaa")

    def test_target_dict(self):
        url = "https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets"
        t = Target(url)
        self.assertTrue("@context" in t)
        del t["@context"]
        self.assertTrue("@context" not in dict(t))

    def test_target_len(self):
        t = Target("https://translate.yandex.ru?value.lang=en-ru&value.text=Targets")
        self.assertTrue(len(t) == 3)

    def test_target_spot(self):
        t = Target({
            "spot": "public",
            "base": "url",
            "entity": "https://translate.yandex.ru?value.lang=en-ru&value.text=Targets"
        })
        self.assertTrue(len(t) == 3)

    def test_target_clear(self):
        t = Target("public", "url", "https://translate.yandex.ru?value.lang=en-ru&value.text=Targets")
        t.clear()
        self.assertTrue(len(t) == 0)

    def test_reference_init_unique(self):
        t = Reference([
            Target("https://en.wikipedia.org/wiki/Object_database"),
            "https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets"
        ], unique=True)
        t.append(Target(
            {'spot': 'https', 'base': 'translate.yandex.ru', '@type': '/',
             '@context': {'value': {'lang': 'en-ru', 'text': 'Targets'}}}
        ))
        t.insert(0, Target("https://en.wikipedia.org/wiki/Object_database"))
        self.assertTrue(len(t) == 2)

    def test_reference_init(self):
        t = Reference([
            Target("https://en.wikipedia.org/wiki/Object_database"),
            "https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets"
        ], unique=False)
        t.append(Target(
            {'spot': 'https', 'base': 'translate.yandex.ru', '@type': '/',
             '@context': {'value': {'lang': 'en-ru', 'text': 'Targets'}}}
        ))
        t.insert(0, Target("https://en.wikipedia.org/wiki/Object_database"))
        self.assertTrue(len(t) == 4)

    def test_reference_unique_init(self):
        t = Reference(
            [
                "project:[\"mcode-cc\",\"xshl\"]@pypi.org/xshl-target/#https://xshl.org/schemas/1.1/definitions/target.json",
                "https://github.com/mcode-cc/py-xshl-target",
                "https://en.wikipedia.org/wiki/Object_database",
                "https://translate.yandex.ru?value.lang=en-ru&value.text=Targets",
                "https://en.wikipedia.org/wiki/Object_database"
            ],
            unique=True
        )
        t.insert(0, Target("https://github.com/mcode-cc/py-xshl-target"))
        t.append(
            Target(
                **{
                    "@id": "https://xshl.org/schemas/1.1/definitions/target.json",
                    "@type": "/xshl-target/",
                    "base": "pypi.org",
                    "entity": [
                        "mcode-cc",
                        "xshl"
                    ],
                    "spot": "project"
                }
            )
        )
        self.assertTrue(len(t) == 4)

    def test_reference_unique_append(self):
        t = Reference(
            [
                "https://github.com/mcode-cc/py-xshl-target",
                "https://en.wikipedia.org/wiki/Object_database",
                "https://translate.yandex.ru?value.lang=en-ru&value.text=Targets",
                "https://en.wikipedia.org/wiki/Object_database"
            ],
            unique=True
        )
        value0 = Target(
            **{
                "@id": "https://xshl.org/schemas/1.1/definitions/target.json",
                "@type": "/xshl-target/",
                "base": "pypi.org",
                "entity": [
                    "mcode-cc",
                    "xshl"
                ],
                "spot": "project"
            }
        )

        t.append(value0)
        value2 = t.append(
            Target(
                "project:[\"mcode-cc\",\"xshl\"]@pypi.org/xshl-target/"
                "#https://xshl.org/schemas/1.1/definitions/target.json"
            )
        )
        self.assertTrue(value0 is value2)

    def test_reference_unique_insert(self):
        t = Reference(
            [
                "https://en.wikipedia.org/wiki/Object_database",
                "https://translate.yandex.ru?value.lang=en-ru&value.text=Targets",
                "https://en.wikipedia.org/wiki/Object_database"
            ],
            unique=True
        )
        value0 = Target("https://github.com/mcode-cc/py-xshl-target")
        t.insert(0, value0)
        value2 = t.insert(1, Target("https://github.com/mcode-cc/py-xshl-target"))
        self.assertTrue(value0 is value2)
        self.assertTrue(t[1].sid == t[value2.sid].sid)
        self.assertTrue(t.index(value0) == 1)

    def test_reference_delete(self):
        t = Reference(
            [
                "https://en.wikipedia.org/wiki/Object_database",
                "https://translate.yandex.ru?value.lang=en-ru&value.text=Targets"
            ],
            unique=True
        )
        value0 = Target("https://github.com/mcode-cc/py-xshl-target")
        t.insert(0, value0)
        del t[0]
        self.assertTrue(value0 not in t)

    def test_groot_unique_insert(self):
        g = GRoot()
        for t in [
            "https://en.wikipedia.org/wiki/Object_database",
            "https://translate.yandex.ru?value.lang=en-ru&value.text=Targets",
            "https://en.wikipedia.org/wiki/Object_database"
        ]:
            g.append(Target(t))
        value0 = Target("https://github.com/mcode-cc/py-xshl-target")
        g.insert(0, value0)
        value2 = g.insert(1, Target("https://github.com/mcode-cc/py-xshl-target"))
        self.assertTrue(value0 is value2)
        self.assertTrue(g[1].sid == g[value2.sid].sid)
        self.assertTrue(g.index(value0) == 1)

    def test_arborescences(self):
        a = GRoot()
        root = Target("a:b@c")
        a.append(Target("n:b@root"), root)
        a.append(Target("n:a@root"), root)
        a.append(Target("n:c@root"), root)
        a.append(Target("n:x@c"), Target("n:c@root"))
        a.append(Target("n:y@c"), Target("n:c@root"))
        self.assertTrue(list(a.topology(reverse=True))[-1] == root)
        self.assertTrue(len(list(a.requirements(Target("n:c@root")))) == 2)

    def test_wind_unwind(self):
        a = {
            "a": {
                "b": {
                    "c": [
                        {"bar": 1, "foo": 2},
                        {"bar": 4, "foo": 3}
                    ]
                }
            }

        }
        b = unwind(a)
        c = wind(b)
        self.assertTrue(b["a.b.c.1.foo"] == c["a"]["b"]["c"][1]["foo"])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)
