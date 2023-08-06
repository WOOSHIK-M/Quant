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

#### Use dashboard
```bash
# use dashboard
> python main.py run --dashboard
```

<img width="1675" alt="image" src="https://github.com/WOOSHIK-M/Quant/assets/44994859/2ffe91a9-d713-4384-ae49-9b7d1a878234">

