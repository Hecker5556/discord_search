import aiohttp, asyncio
from aiohttp_socks import ProxyConnector
from datetime import datetime, timedelta
import json
class discord_search:
    async def lazy_search(token: str, return_msgs: bool = False, proxy: str = None, amount: int = None, **kwargs) -> (list[int] | list[dict]):
        """
        Args:

            token (str) - user token to use with search api requests

            return_msgs (bool, False) - whether to return entire message objects

            proxy (str, optional) - proxy to use

            amount(int, optional) - amount of messages to get, by default all

            guild_id (int) - which guild to search in
            
            text (str, optional) - text to search for
            
            from_user (int, optional) - messages from a user id
            
            in_channel (int, optional) - messages in a channel

            mentions (int, optional) - messages that mention that user id
            
            has ('link', 'embed', 'file', 'video', 'image', 'sound', 'sticker', optional) - messages that include one of those things
            
            before (datetime object, optional) - messages before a date
            
            during (datetime object, optional) - messages during a date
            
            after (datetime object, optional)  - messages after a date
            
            pinned (bool, optional) - messages that are pinned

            include_nsfw (bool, True) - messages that are in nsfw channels

            new (bool, optional) - newest messages

            old (bool, optional) - oldest messages

            relevant (bool, optional) - relevant messages

            offset (int, optional) - starting offset

        Returns:

            On iteration a list of a number of  message ids

            OR

            On iterationa  list of message dicts
        """
        if amount and amount < 0:
            raise ValueError("amount needs to be a positive number (larger than 0)!")
        params = {}
        params['include_nsfw'] = str(True)
        url = None
        customoffset = False
        for key, value in kwargs.items():
            match key:
                case "guild_id":
                    url = f"https://canary.discord.com/api/v9/guilds/{value}/messages/search"
                case "text":
                    if not value:
                        continue
                    params['content'] = value
                case "from_user":
                    if not value:
                        continue
                    params['author_id'] = value
                case "mentions":
                    if not value:
                        continue
                    params['mentions'] = value
                case "has":
                    if not value:
                        continue
                    if value.lower() not in ['link', 'embed', 'file', 'video', 'image', 'sound', 'sticker']:
                        continue
                    params['has'] = value
                case 'before':
                    if not value:
                        continue
                    if not isinstance(value, datetime):
                        continue
                    params['max_id'] = discord_search.convert_to_snowflake(value)
                case 'during':
                    if not value:
                        continue
                    if not isinstance(value, datetime):
                        continue
                    params['max_id'] = discord_search.convert_to_snowflake(value + timedelta(days=1)) #before day + 1
                    params['min_id'] = discord_search.convert_to_snowflake(value - timedelta(days=1)) #after day - 1
                case 'after':
                    if not value:
                        continue
                    if not isinstance(value, datetime):
                        continue
                    params['min_id'] = discord_search.convert_to_snowflake(value)
                case 'pinned':
                    if not value:
                        continue
                    if isinstance(value, bool):
                        params['pinned'] = str(value)
                case 'include_nsfw':
                    if not value:
                        continue
                    params['include_nsfw'] = str(value)
                case 'in_channel':
                    if not value:
                        continue
                    params['channel_id'] = value
                case 'relevant':
                    if not value:
                        continue
                    params['sort_by'] = 'relevance'
                    params['sort_order'] = 'desc'
                case 'new':
                    if not value:
                        continue
                    params['sort_by'] = 'timestamp'
                    params['sort_order'] = 'desc'
                case 'old':
                    if not value:
                        continue
                    params['sort_by'] = 'timestamp'
                    params['sort_order'] = 'asc'
                case 'offset':
                    if not value:
                        continue
                    params['offset'] = value
                    customoffset = True
                case _:
                    print("invalid argument: %s" % key)
        if len(params.keys()) <= 1:
            raise ValueError("provide arguments!")
        if not url:
            raise ValueError("no guild id provided! provide guild id by passing guild_id=id in the function")
        headers = {
            'authority': 'canary.discord.com',
            'accept': '*/*',
            'accept-language': 'en-US,pl;q=0.9,ru;q=0.8',
            'authorization': token,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.175 Chrome/120.0.6099.268 Electron/28.2.1 Safari/537.36',
        }
        if not amount:
            async with aiohttp.ClientSession(connector=discord_search.make_connector(proxy)) as session:
                messages_json = await discord_search.make_request(url, params, headers, session)
                parsed: dict = discord_search.parse_messages(messages_json, return_msgs)
                total = parsed.get('total_results')
                total -= len(parsed['messages'])
                start = 25
                yield parsed['messages'], parsed['total_results']
                while total > 0:
                    if not customoffset:
                        params['offset'] = start
                    else:
                        params['offset'] += start
                    messages_json = await discord_search.make_request(url, params, headers, session)
                    parsed: dict = discord_search.parse_messages(messages_json, return_msgs)
                    total -= len(parsed['messages'])
                    yield parsed['messages'], parsed['total_results']
                    start += 25
        else:
            start = 25
            left = amount
            isfirst = True
            async with aiohttp.ClientSession(connector=discord_search.make_connector(proxy)) as session:
                while left > 0:
                    if not isfirst:
                        if not customoffset:
                            params['offset'] = start
                        else:
                            params['offset'] += start
                    messages_json = await discord_search.make_request(url, params, headers, session)
                    parsed: dict = discord_search.parse_messages(messages_json, return_msgs)
                    yield parsed['messages'][:left], parsed['total_results']
                    left -= len(parsed['messages'])
                    if isfirst:
                        total = parsed['total_results'] - len(parsed['messages'])
                        isfirst = False
                        if total == 0:
                            break
                    else:
                        total -= len(parsed['messages'])
                        if total == 0:
                            break
                        start += 25
    async def search(token: str, return_msgs: bool = False, proxy: str = None, amount: int = None, **kwargs) -> (list[int] | list[dict]):
        """
        Args:

            token (str) - user token to use with search api requests

            return_msgs (bool, False) - whether to return entire message objects

            proxy (str, optional) - proxy to use

            amount(int, optional) - amount of messages to get, by default all

            guild_id (int) - which guild to search in
            
            text (str, optional) - text to search for
            
            from_user (int, optional) - messages from a user id
            
            in_channel (int, optional) - messages in a channel

            mentions (int, optional) - messages that mention that user id
            
            has ('link', 'embed', 'file', 'video', 'image', 'sound', 'sticker', optional) - messages that include one of those things
            
            before (datetime object, optional) - messages before a date
            
            during (datetime object, optional) - messages during a date
            
            after (datetime object, optional)  - messages after a date
            
            pinned (bool, optional) - messages that are pinned

            include_nsfw (bool, True) - messages that are in nsfw channels

            new (bool, optional) - newest messages

            old (bool, optional) - oldest messages

            relevant (bool, optional) - relevant messages

            offset (int, optional) - starting offset

        Returns:

            A list of all the message ids

            OR

            A list of all message dicts
        """
        if amount and amount < 0:
            raise ValueError("amount needs to be a positive number (larger than 0)!")
        params = {}
        params['include_nsfw'] = str(True)
        url = None
        customoffset = False
        for key, value in kwargs.items():
            match key:
                case "guild_id":
                    url = f"https://canary.discord.com/api/v9/guilds/{value}/messages/search"
                case "text":
                    if not value:
                        continue
                    params['content'] = value
                case "from_user":
                    if not value:
                        continue
                    params['author_id'] = value
                case "mentions":
                    if not value:
                        continue
                    params['mentions'] = value
                case "has":
                    if not value:
                        continue
                    if value.lower() not in ['link', 'embed', 'file', 'video', 'image', 'sound', 'sticker']:
                        continue
                    params['has'] = value
                case 'before':
                    if not value:
                        continue
                    if not isinstance(value, datetime):
                        continue
                    params['max_id'] = discord_search.convert_to_snowflake(value)
                case 'during':
                    if not value:
                        continue
                    if not isinstance(value, datetime):
                        continue
                    params['max_id'] = discord_search.convert_to_snowflake(value + timedelta(days=1)) #before day + 1
                    params['min_id'] = discord_search.convert_to_snowflake(value - timedelta(days=1)) #after day - 1
                case 'after':
                    if not value:
                        continue
                    if not isinstance(value, datetime):
                        continue
                    params['min_id'] = discord_search.convert_to_snowflake(value)
                case 'pinned':
                    if not value:
                        continue
                    if isinstance(value, bool):
                        params['pinned'] = str(value)
                case 'include_nsfw':
                    if not value:
                        continue
                    params['include_nsfw'] = str(value)
                case 'in_channel':
                    if not value:
                        continue
                    params['channel_id'] = value
                case 'relevant':
                    if not value:
                        continue
                    params['sort_by'] = 'relevance'
                    params['sort_order'] = 'desc'
                case 'new':
                    if not value:
                        continue
                    params['sort_by'] = 'timestamp'
                    params['sort_order'] = 'desc'
                case 'old':
                    if not value:
                        continue
                    params['sort_by'] = 'timestamp'
                    params['sort_order'] = 'asc'
                case 'offset':
                    if not value:
                        continue
                    params['offset'] = value
                    customoffset = True
                case _:
                    print("invalid argument: %s" % key)
        if len(params.keys()) <= 1:
            raise ValueError("provide arguments!")
        if not url:
            raise ValueError("no guild id provided! provide guild id by passing guild_id=id in the function")
        headers = {
            'authority': 'canary.discord.com',
            'accept': '*/*',
            'accept-language': 'en-US,pl;q=0.9,ru;q=0.8',
            'authorization': token,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.175 Chrome/120.0.6099.268 Electron/28.2.1 Safari/537.36',
        }
        messages = []
        if not amount:
            async with aiohttp.ClientSession(connector=discord_search.make_connector(proxy)) as session:
                messages_json = await discord_search.make_request(url, params, headers, session)
                parsed: dict = discord_search.parse_messages(messages_json, return_msgs)
                total = parsed.get('total_results')
                total -= len(parsed['messages'])
                start = 25
                messages += parsed['messages']
                while total > 0:
                    if not customoffset:
                        params['offset'] = start
                    else:
                        params['offset'] += start
                    messages_json = await discord_search.make_request(url, params, headers, session)
                    parsed: dict = discord_search.parse_messages(messages_json, return_msgs)
                    total -= len(parsed['messages'])
                    messages += parsed['messages']
                    start += 25
        else:
            start = 25
            left = amount
            isfirst = True
            async with aiohttp.ClientSession(connector=discord_search.make_connector(proxy)) as session:
                while left > 0:
                    if not isfirst:
                        if not customoffset:
                            params['offset'] = start
                        else:
                            params['offset'] += start
                    messages_json = await discord_search.make_request(url, params, headers, session)
                    parsed: dict = discord_search.parse_messages(messages_json, return_msgs)
                    left -= len(parsed['messages'])
                    messages += parsed['messages']
                    if isfirst:
                        total = parsed['total_results'] - len(parsed['messages'])
                        isfirst = False
                        if total == 0:
                            break
                    else:
                        total -= len(parsed['messages'])
                        if total == 0:
                            break
                        start += 25
                messages = messages[:amount]
        return messages, parsed['total_results']
    def make_connector(proxy: str) -> (ProxyConnector | aiohttp.TCPConnector):
        if proxy:
            if "socks" in proxy:
                return ProxyConnector.from_url(proxy)
            else:
                return aiohttp.TCPConnector(proxy=proxy)
        else:
            return aiohttp.TCPConnector()
    async def make_request(url: str, params: dict, headers: dict, session: aiohttp.ClientSession):
        while True:
            async with session.get(url, headers=headers, params=params) as r:
                if r.status == 403:
                    raise ValueError("Status 403 forbidden! Check your guild_id, perms")
                if r.status == 401:
                    raise ValueError("Status 401 unauthorized! Check your token")
                rtext = await r.text(encoding="utf-8")
                parsed = json.loads(rtext)
                if parsed.get('retry_after'):
                    print(f"ratelimited {parsed['retry_after']}")
                    await asyncio.sleep(parsed['retry_after'])
                    continue
                return parsed
    def convert_to_snowflake(date: datetime) -> int:
        timestamp = int(date.timestamp()*1000)
        timestamp = (timestamp - 1420070400000) << 22
        snowflake = timestamp or 0
        return str(snowflake)
    def parse_messages(messages: dict, return_msgs: bool = False) -> dict:
        parsed = {}
        total = messages.get('total_results')
        parsed['total_results'] = total
        if not return_msgs:
            parsed['messages'] = []
            for message in messages.get('messages'):
                parsed['messages'].append(message[0].get('id'))
        else:
            parsed['messages'] = []
            for message in messages.get('messages'):
                parsed['messages'].append(message[0])
        return parsed
async def main():
    msgs = []
    async for msg, total in discord_search.lazy_search(in_channel=1006349799039189072, amount=5, offset=324, token=token, guild_id=guild_id, return_msgs = True):
        msgs.append(msg)

    with open("messages.json", "w") as f1:
        json.dump(msgs, f1)
if __name__ == "__main__":
    from env import token, guild_id
    from pprint import pprint
    # result = asyncio.run(discord_search.search(in_channel=1006349799039189072, token=token, guild_id=guild_id, amount=None, return_msgs = True))
    asyncio.run(main())
    # with open("messages.json", "w") as f1:
    #     json.dump(result, f1, indent=4)
    # print(len(result))