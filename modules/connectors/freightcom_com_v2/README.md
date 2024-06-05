
# karrio.freightcom_com_v2

This package is a Frieghtcom v2 extension of the [karrio](https://pypi.org/project/karrio) multi carrier shipping SDK.

## Requirements

`Python 3.7+`

## Installation

```bash
pip install karrio.freightcom_com_v2
```

## Usage

```python
import karrio
from karrio.mappers.freightcom_com_v2.settings import Settings


# Initialize a carrier gateway
freightcom_com_v2 = karrio.gateway["freightcom_com_v2"].create(
    Settings(
        ...
    )
)
```

Check the [Karrio Mutli-carrier SDK docs](https://docs.karrio.io) for Shipping API requests
