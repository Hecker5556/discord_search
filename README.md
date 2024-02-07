# Simple discord search function implemented in python
Includes:
-   from_user
-   text
-   in_channel
-   mentions
-   has 
-   before
-   during
-   after
-   pinned
-   include_nsfw

Others:
-   proxy
-   amount
-   return_msgs

Returns:
A list of message ids or a list of messages in json format

## Setup
download [python](https://python.org/downloads)

I used 3.10.9

in cmd
```bash
git clone https://github.com/Hecker5556/discord_search
```
```bash
cd discord_search
```
```bash
pip install -r requirements.txt
```

## Usage

Only in python

```python
#assuming discord_search is in path
from discord_search import discord_search

#in non async
import asyncio
results = asyncio.run(discord_search.search(text="hi", token=token, guild_id=guild_id))

#in async
async def main():
    results = await discord_search.search(text="hi", token=token, guild_id=guild_id)
```