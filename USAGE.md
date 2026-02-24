<!-- Start SDK Example Usage [usage] -->
```python
# Synchronous Example
from spaire_sdk import Spaire


with Spaire(
    access_token="<YOUR_BEARER_TOKEN_HERE>",
) as spaire:

    res = spaire.organizations.list(page=1, limit=10)

    while res is not None:
        # Handle items

        res = res.next()
```

</br>

The same SDK client can also be used to make asynchronous requests by importing asyncio.

```python
# Asynchronous Example
import asyncio
from spaire_sdk import Spaire

async def main():

    async with Spaire(
        access_token="<YOUR_BEARER_TOKEN_HERE>",
    ) as spaire:

        res = await spaire.organizations.list_async(page=1, limit=10)

        while res is not None:
            # Handle items

            res = res.next()

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->