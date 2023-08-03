# Auto-trading project

It uses [Upbit API](https://docs.upbit.com/docs).

### Installation

```bash
# create conda env or pyenv first
# it supports the python versions 3.9 or 3.10
> make init
```

### API keys

```python
# make api data class in ./api_keys.py
from dataclasses import dataclass


@dataclass
class PersonalKeys:
    access_key: str = ""
    secret_key: str = ""
```

### How to use?

```bash
# use dashboard
> python main.py run --dashboard
```
