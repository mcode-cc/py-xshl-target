import unittest
from xshl.target import Target, Targets


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
        self.assertTrue(t["@context"]["value"]["text"] == "Targets")
        self.assertTrue(str(t) == url)

    def test_target_dict(self):
        url = "https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets"
        t = Target(url)
        self.assertTrue("@context" in t)
        del t["@context"]
        self.assertTrue("@context" not in dict(t))

    def test_target_len(self):
        url = "#https://translate.yandex.ru?value.lang=en-ru&value.text=Targets"
        t = Target(url)
        print(len(t))
        del t["@context"]
        self.assertTrue("@context" not in dict(t))

    def test_targets_init_unique(self):
        t = Targets([
            Target("https://en.wikipedia.org/wiki/Object_database"),
            "https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets"
        ], unique=True)
        t.append(Target(
            {'spot': 'https', 'base': 'translate.yandex.ru', '@type': '/',
             '@context': {'value': {'lang': 'en-ru', 'text': 'Targets'}}}
        ))
        t.insert(0, Target("https://en.wikipedia.org/wiki/Object_database"))
        self.assertTrue(len(t) == 2)

    def test_targets_init(self):
        t = Targets([
            Target("https://en.wikipedia.org/wiki/Object_database"),
            "https://translate.yandex.ru/?value.lang=en-ru&value.text=Targets"
        ], unique=False)
        t.append(Target(
            {'spot': 'https', 'base': 'translate.yandex.ru', '@type': '/',
             '@context': {'value': {'lang': 'en-ru', 'text': 'Targets'}}}
        ))
        t.insert(0, Target("https://en.wikipedia.org/wiki/Object_database"))
        self.assertTrue(len(t) == 4)

    def test_targets_unique_init(self):
        t = Targets(
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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)
