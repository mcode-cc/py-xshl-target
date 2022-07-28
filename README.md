[![PyPI](https://img.shields.io/pypi/v/xshl-target)](https://pypi.org/project/xshl-target/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/xshl-target)
[![PyPI - License](https://img.shields.io/pypi/l/xshl-target)](https://github.com/mcode-cc/py-xshl-target/blob/main/LICENSE)


# Python Library for XSHL Target

[JSON Schema](https://xshl.org/schemas/1.1/definitions/target.json) 


```python
import json
from xshl.target import Target, Targets

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
print(json.dumps(t.dictionaries, ensure_ascii=False, sort_keys=True, indent=4))
```

```json
[
    {
        "@id": "https://xshl.org/schemas/1.1/definitions/target.json",
        "@type": "/xshl-target/",
        "base": "pypi.org",
        "entity": [
            "mcode-cc",
            "xshl"
        ],
        "spot": "project"
    },
    {
        "@type": "/mcode-cc/py-xshl-target",
        "base": "github.com",
        "spot": "https"
    },
    {
        "@type": "/wiki/Object_database",
        "base": "en.wikipedia.org",
        "spot": "https"
    },
    {
        "@context": {
            "value": {
                "lang": "en-ru",
                "text": "Targets"
            }
        },
        "base": "translate.yandex.ru",
        "spot": "https"
    }
]
```