import aiohttp
import asyncio

from .models import User


class OsuClient:

    def __init__(self, key, loop=None, session=None):
        self.key = key
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=self.loop)

    def user_type(self, user):
        if user is None:
            return None
        return "id" if isinstance(user, int) else "string"

    async def close(self):
        await self.session.close()

    async def request(self, endpoint, data, retries=5):
        while retries:
            resp = await self.session.get(endpoint, params=data)
            try:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                elif resp.status == 504:
                    retries -= 1
                else:
                    break
            finally:
                resp.close()

    async def get_user(self, user, event_days=31):
        user = await self.request("https://osu.ppy.sh/api/get_user",
                                  dict(
                                    k=self.key,
                                    u=user,
                                    type=self.user_type(user),
                                    m=0,
                                    event_days=event_days
                                  ))
        return User(user[0])
